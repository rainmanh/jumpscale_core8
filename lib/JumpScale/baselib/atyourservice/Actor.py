from JumpScale import j

import copy
import inspect
import imp
import sys

from JumpScale.baselib.atyourservice.models.ActorModel import ActorModel
from JumpScale.baselib.atyourservice.ActorTemplate import ActorTemplate
from JumpScale.baselib.atyourservice.Service import Service

DECORATORCODE = """
ActionsBase=j.atyourservice.getActionsBaseClass()

"""

modulecache = {}


def loadmodule(name, path):
    key = path
    if key in modulecache:
        return modulecache[key]
    parentname = ".".join(name.split(".")[:-1])
    sys.modules[parentname] = __package__
    mod = imp.load_source(name, path)
    modulecache[key] = mod
    return mod


class Actor(ActorTemplate):

    def __init__(self, aysrepo, template):
        """
        """

        self.template = template
        self.aysrepo = aysrepo

        self.name = aysrepo.name

        self.path = j.sal.fs.joinPaths(aysrepo.path, "actors", template.name)

        self.logger = j.atyourservice.logger

        self._init_props()

        if j.atyourservice.db.actor.exists(self.name):
            self.model = j.atyourservice.db.actor.new()
            self.model.dbobj.name = self.name
        else:
            self.model = j.atyourservice.db.actor.get(key=self.name)
            self.model.dbobj.name = self.name

        # copy the files
        if not j.sal.fs.exists(path=self.path):
            self.loadFromFS()

        self.model.save()

    @property
    def schema(self):
        if self._schema is None:
            self._schema = j.data.hrd.getSchema(content=self.model.dbobj.serviceDataSchema)
        return self._schema

# INIT

    def loadFromFS(self):
        """
        get content from fs and load in object
        """
        self.copyFilesFromTemplates()
        from IPython import embed
        print("DEBUG NOW sdsds")
        embed()
        raise RuntimeError("stop debug here")
        if j.sal.fs.exists(self.path_hrd_schema):
            # self.model.dbobj.serviceDataSchema = j.sal.fs.fileGetContents(self.path_hrd_schema)
            from IPython import embed
            print("DEBUG NOW hrd schema in actor")
            embed()
            raise RuntimeError("stop debug here")

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

        if j.sal.fs.exists(self.template.path_actions):
            content = j.sal.fs.fileGetContents(self.template.path_actions)
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
                self.addAction(amName, amSource, amDecorator, amMethodArgs)
                amSource = ""
                amName = ""
                amDecorator = ""
                amMethodArgs = {}
                continue

            if state is not "INIT" and linestrip.startswith("@"):
                amDecorator = linestrip
                continue

            if state == "MAIN" and linestrip.startswith("def"):
                state = "DEF"
                from IPython import embed
                print("DEBUG NOW defline")
                embed()
                raise RuntimeError("stop debug here")
                amMethodArgs
                amName = linestrip.split("(", 1)[0][4:].strip()
                if amDecorator == "":
                    if amName in actorMethods:
                        amDecorator = "@actor"
                    else:
                        amDecorator = "@service"
                continue

            if state == "DEF":
                amSource += "%s\n" % line[4:]

        # process the last one
        if amName != "":
            self.addAction(amName, amSource, amDecorator, amMethodArgs)

        for actionname in actionmethodsRequired:
            if actionname not in self.model.actionsSortedList:
                # self.addAction(name=actionname, isDefaultMethod=True)
                # not found
                if actionname == "input":
                    self.addAction(amName="input", amSource="", amDecorator="actor",
                                   amMethodArgs={"service": "", "name": "", "role": "", "instance": ""})
                else:
                    self.addAction(amName=actionname, amSource="", amDecorator="service",
                                   amMethodArgs={"service": ""})

        # add missing methods
        j.sal.fs.writeFile(self.path_actions, self.model.actionsSourceCode)

    def addAction(self, amName, amSource, amDecorator, amMethodArgs):
        actionKey = j.data.hash.blake2_string(self.name + amSource)
        change = False
        if not j.atyourservice.db.actionCode.exists(actionKey):
            # need to create new object
            change = True
            ac = j.atyourservice.db.actionCode.new()
            ac.dbobj.code = amSource
            ac.dbobj.actorName = self.name
            ac.dbobj.guid = actionKey
            ac.dbobj.name = amName
            for key, val in amMethodArgs.items():
                ac.argAdd(key, val)  # will check for duplicates
            ac.dbobj.lastModDate = j.data.time.epoch

        from IPython import embed
        print("DEBUG addAction ")
        embed()
        raise RuntimeError("stop debug here")
        # actionAdd(self, name, actionCodeKey="", type="service")

# SERVICE
    def _serviceTemplateActionsGet(self):
        path_actions = j.sal.fs.joinPaths(self.path, "actions.py")
        modulename = "JumpScale.atyourservice.%s.servicetemplate" % (self.name)
        mod = loadmodule(modulename, path_actions)
        return mod.Actions()

    def _actorActionsGet(self, service):
        path_actions = j.sal.fs.joinPaths(self.path, "actions_actor.py")
        modulename = "JumpScale.atyourservice.%s.%s.actor" % (self.name)
        mod = loadmodule(modulename, path_actions)
        return mod.Actions()

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
    def upload2AYSfs(self, path):
        """
        tell the ays filesystem about this directory which will be uploaded to ays filesystem
        """
        j.tools.sandboxer.dedupe(
            path, storpath="/tmp/aysfs", name="md", reset=False, append=True)

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
