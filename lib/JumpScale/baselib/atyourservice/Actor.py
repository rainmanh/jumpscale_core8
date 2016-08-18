from JumpScale import j

import copy
import inspect
import imp
import sys
import capnp

from JumpScale.baselib.atyourservice.models.ActorModel import ActorModel
from JumpScale.baselib.atyourservice.ActorTemplate import ActorTemplate, ActorBase
from JumpScale.baselib.atyourservice.Service import Service

DECORATORCODE = """
ActionsBase=j.atyourservice.getActionsBaseClass()

"""


class Actor(ActorBase):

    def __init__(self, aysrepo, template):
        """
        """

        self.template = template
        self.aysrepo = aysrepo

        self.path = j.sal.fs.joinPaths(aysrepo.path, "actors", template.name)

        self.logger = j.atyourservice.logger

        self.name = self.template.name

        self._init_props()
        self._schema = None

        if j.atyourservice.db.actor.exists(template.name):
            self.model = j.atyourservice.db.actor.new()
        else:
            self.model = j.atyourservice.db.actor.get(key=template.name)

        self.model.dbobj.name = self.name

        # copy the files
        if not j.sal.fs.exists(path=self.path):
            self.loadFromFS()

    @property
    def schema(self):
        if self._schema is None:
            self._schema = capnp.load(self.path_capnp_schema_actor)
        return self._schema

# INIT

    def loadFromFS(self):
        """
        get content from fs and load in object
        """
        self.copyFilesFromTemplates()
        self.logger.debug("loading actor: %s" % self)
        # hrd schema to capnp
        j.sal.fs.writeFile(self.path_capnp_schema_actor, self.template.schemaActor.capnpSchema)
        if j.sal.fs.exists(self.path_hrd_schema_actor):
            if self.model.dbobj.actorDataSchema != self.template.schemaActor.capnpSchema:
                self.processChange("schema_actor")
                self.model.dbobj.actorDataSchema = self.template.schemaActor.capnpSchema
        if j.sal.fs.exists(self.path_hrd_schema_service):
            if self.model.dbobj.serviceDataSchema != self.template.schemaService.capnpSchema:
                self.processChange("schema_service")
                self.model.dbobj.serviceDataSchema = self.template.schemaService.capnpSchema

        scode = self.model.actionsSourceCode
        self.model.save()

    def copyFilesFromTemplates(self):
        j.sal.fs.createDir(self.path)
        # look for all keys which start with path_ copy these from template to local actor in fs
        for key in self.__dict__.keys():
            if key.startswith("path_"):
                if j.sal.fs.exists(self.template.__dict__[key], followlinks=True):
                    j.sal.fs.copyFile(self.template.__dict__[key], self.__dict__[key])

        self._processActionsFile()

    def _processActionsFile(self):
        self._out = ""

        actionmethodsRequired = ["input", "init", "install", "stop", "start", "monitor", "halt", "check_up", "check_down",
                                 "check_requirements", "cleanup", "data_export", "data_import", "uninstall", "removedata", "consume"]

        actorMethods = ["input", "build"]

        if j.sal.fs.exists(self.template._path_actions):
            content = j.sal.fs.fileGetContents(self.template._path_actions)
        else:
            content = "class Actions(ActionsBase):\n\n"

        if content.find("class action(ActionMethodDecorator)") != -1:
            raise j.exceptions.Input("There should be no decorator specified in %s" % self.path_actions)

        content = "%s\n\n%s" % (DECORATORCODE, content)

        content = content.replace("from JumpScale import j", "")
        content = "from JumpScale import j\n\n%s" % content

        state = "INIT"
        amSource = ""
        amName = ""
        amDecorator = ""
        amMethodArgs = {}

        # DO NOT CHANGE TO USE PYTHON PARSING UTILS
        lines = content.splitlines()

        for line in lines:
            linestrip = line.strip()
            if state == "INIT" and linestrip.startswith("class Actions"):
                state = "MAIN"
                continue

            if state == "DEF" and (linestrip.startswith("@") or linestrip.startswith("def")):
                # means we are at end of def to new one
                self._addAction(amName, amSource, amDecorator, amMethodArgs)
                amSource = ""
                amName = ""
                amDecorator = ""
                amMethodArgs = {}
                state = 'MAIN'

            if state is not "INIT" and linestrip.startswith("@"):
                amDecorator = linestrip
                continue

            if state == "MAIN" and linestrip.startswith("def"):
                definition, args = linestrip.split("(", 1)
                args = args.rstrip('):')
                for arg in args.split(','):
                    if '=' in arg:
                        argname, default = arg.split('=', 1)
                    else:
                        argname = arg
                        default = ""
                    amMethodArgs[argname.strip()] = default.strip()
                amName = definition[4:].strip()
                self.logger.debug('amName: %s' % amName)
                if amDecorator == "":
                    if amName in actorMethods:
                        amDecorator = "@actor"
                    else:
                        amDecorator = "@service"
                state = "DEF"
                continue

            if state == "DEF":
                amSource += "%s\n" % line[4:]

        # process the last one
        if amName != "":
            self._addAction(amName, amSource, amDecorator, amMethodArgs)

        for actionname in actionmethodsRequired:
            if actionname not in self.model.actionsSortedList:
                # self.addAction(name=actionname, isDefaultMethod=True)
                # not found
                if actionname == "input":
                    self._addAction(amName="input", amSource="", amDecorator="actor",
                                    amMethodArgs={"service": "", "name": "", "role": "", "instance": ""})
                else:
                    self._addAction(amName=actionname, amSource="", amDecorator="service",
                                    amMethodArgs={"service": ""})

        # add missing methods
        j.sal.fs.writeFile(self._path_actions, self.model.actionsSourceCode)

    def _addAction(self, amName, amSource, amDecorator, amMethodArgs):
        actionKey = j.data.hash.md5_string(self.name + amName + amSource)
        if not j.atyourservice.db.actionCode.exists(actionKey):
            # need to create new object
            ac = j.atyourservice.db.actionCode.new()
            ac.dbobj.code = amSource
            ac.dbobj.actorName = self.name
            ac.dbobj.guid = actionKey
            ac.dbobj.name = amName
            for key, val in amMethodArgs.items():
                ac.argAdd(key, val)  # will check for duplicates
            ac.dbobj.lastModDate = j.data.time.epoch
            ac.save()

        if amName in ["init", "build"]:
            atype = 'actor'
        else:
            atype = 'service'

        oldaction = self.model.actionGet(amName)
        if oldaction is None:
            self.processChange("action_%s" % amName)
            self.model.actionAdd(amName, actionCodeKey=actionKey, type=atype)
        elif oldaction.actionCodeKey != actionKey:
            self.processChange("action_%s" % amName)
            oldaction.actionCodeKey = actionKey

    def processChange(self, changeCategory):
        """e.g. action_install"""
        # TODO: implement change mgmt
        pass

# SERVICE

    def serviceCreate(self, instance="main", args={}, path='', parent=None, consume="", originator=None, model=None):
        """
        """
        if parent is not None and instance == "main":
            instance = parent.instance

        instance = instance.lower()

        service = self.aysrepo.serviceGet(role=self.role, instance=instance, die=False)

        if service is not None:
            # print("NEWINSTANCE: Service instance %s!%s  exists." % (self.name, instance))
            service._actor = self
            service.init(args=args)
            if model is not None:
                service.model = model
        else:
            key = "%s!%s" % (self.role, instance)

            if path:
                fullpath = path
            elif parent is not None:
                fullpath = j.sal.fs.joinPaths(parent.path, key)
            else:
                ppath = j.sal.fs.joinPaths(self.aysrepo.path, "services")
                fullpath = j.sal.fs.joinPaths(ppath, key)

            if j.sal.fs.isDir(fullpath):
                j.events.opserror_critical(msg='Service with same role ("%s") and of same instance ("%s") is already installed.\nPlease remove dir:%s it could be this is broken install.' % (
                    self.role, instance, fullpath))

            service = Service(aysrepo=self.aysrepo, actor=self, instance=instance,
                              args=args, path="", parent=parent, originator=originator, model=model)

            self.aysrepo._services[service.key] = service

            # service.init(args=args)

        service.consume(consume)

        return service

    @property
    def services(self):
        """
        return a list of instance name for this template
        """
        services = self.aysrepo.findServices(templatename=self.name)
        return [service.instance for service in services]


# GENERIC
    # def upload2AYSfs(self, path):
    #     """
    #     tell the ays filesystem about this directory which will be uploaded to ays filesystem
    #     """
    #     j.tools.sandboxer.dedupe(
    #         path, storpath="/tmp/aysfs", name="md", reset=False, append=True)

    def __repr__(self):
        return "actor: %-15s" % (self.name)

    # def downloadfiles(self):
    #     """
    #     this method download any required files for this actor as defined in the template.hrd
    # Use this method when building a service to have all the files ready to
    # sandboxing

    #     @return list of tuples containing the source and destination of the files defined in the actoritem
    #             [(src, dest)]
    #     """
    #     dirList = []
    #     # download
    #     for actoritem in self.hrd_template.getListFromPrefix("web.export"):
    #         if "dest" not in actoritem:
    # j.events.opserror_critical(msg="could not find dest in hrditem for %s
    # %s" % (actoritem, self), category="ays.actorTemplate")

    #         fullurl = "%s/%s" % (actoritem['url'],
    #                              actoritem['source'].lstrip('/'))
    #         dest = actoritem['dest']
    #         dest = j.application.config.applyOnContent(dest)
    #         destdir = j.sal.fs.getDirName(dest)
    #         j.sal.fs.createDir(destdir)
    #         # validate md5sum
    #         if actoritem.get('checkmd5', 'false').lower() == 'true' and j.sal.fs.exists(dest):
    #             remotemd5 = j.sal.nettools.download(
    #                 '%s.md5sum' % fullurl, '-').split()[0]
    #             localmd5 = j.data.hash.md5(dest)
    #             if remotemd5 != localmd5:
    #                 j.sal.fs.remove(dest)
    #             else:
    #                 continue
    #         elif j.sal.fs.exists(dest):
    #             j.sal.fs.remove(dest)
    #         j.sal.nettools.download(fullurl, dest)

    #     for actoritem in self.hrd_template.getListFromPrefix("git.export"):
    #         if "platform" in actoritem:
    #             if not j.core.platformtype.myplatform.checkMatch(actoritem["platform"]):
    #                 continue

    #         # pull the required repo
    #         dest0 = self.aysrepo._getRepo(actoritem['url'], actoritem=actoritem)
    #         src = "%s/%s" % (dest0, actoritem['source'])
    #         src = src.replace("//", "/")
    #         if "dest" not in actoritem:
    #             j.events.opserror_critical(msg="could not find dest in hrditem for %s %s" % (actoritem, self), category="ays.actorTemplate")
    #         dest = actoritem['dest']

    #         dest = j.application.config.applyOnContent(dest)
    #         src = j.application.config.applyOnContent(src)

    #         if "link" in actoritem and str(actoritem["link"]).lower() == 'true':
    #             # means we need to only list files & one by one link them
    #             link = True
    #         else:
    #             link = False

    #         if src[-1] == "*":
    #             src = src.replace("*", "")
    #             if "nodirs" in actoritem and str(actoritem["nodirs"]).lower() == 'true':
    #                 # means we need to only list files & one by one link them
    #                 nodirs = True
    #             else:
    #                 nodirs = False

    #             items = j.sal.fs.listFilesInDir(
    #                 path=src, recursive=False, followSymlinks=False, listSymlinks=False)
    #             if nodirs is False:
    #                 items += j.sal.fs.listDirsInDir(
    # path=src, recursive=False, dirNameOnly=False,
    # findDirectorySymlinks=False)

    #             raise RuntimeError("getshort_key does not even exist")
    #             items = [(item, "%s/%s" % (dest, j.sal.fs.getshort_key(item)), link)
    #                      for item in items]
    #         else:
    #             items = [(src, dest, link)]

    #         out = []
    #         for src, dest, link in items:
    #             delete = actoritem.get('overwrite', 'true').lower() == "true"
    #             if dest.strip() == "":
    #                 raise j.exceptions.RuntimeError(
    #                     "a dest in codeactor cannot be empty for %s" % self)
    #             if dest[0] != "/":
    #                 dest = "/%s" % dest
    #             else:
    #                 if link:
    #                     if not j.sal.fs.exists(dest):
    #                         j.sal.fs.createDir(j.sal.fs.getParent(dest))
    #                         j.sal.fs.symlink(src, dest)
    #                     elif delete:
    #                         j.sal.fs.remove(dest)
    #                         j.sal.fs.symlink(src, dest)
    #                 else:
    #                     print(("copy: %s->%s" % (src, dest)))
    #                     if j.sal.fs.isDir(src):
    #                         j.sal.fs.createDir(j.sal.fs.getParent(dest))
    #                         j.sal.fs.copyDirTree(
    #                             src, dest, eraseDestination=False, overwriteFiles=delete)
    #                     else:
    #                         j.sal.fs.copyFile(
    #                             src, dest, True, overwriteFile=delete)
    #             out.append((src, dest))
    #             dirList.extend(out)

    #     return dirList
