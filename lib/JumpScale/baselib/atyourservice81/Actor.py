from JumpScale import j
from collections import OrderedDict

# import copy
# import inspect
# import imp
# import sys
import msgpack

# from JumpScale.baselib.atyourservice81.models.ActorModel import ActorModel
# from JumpScale.baselib.atyourservice81.ActorTemplate import ActorTemplate
from JumpScale.baselib.atyourservice81.Service import Service


class Actor():

    def __init__(self, aysrepo, template=None, model=None):
        """
        init from a template or from a model
        """

        self.aysrepo = aysrepo
        self.logger = j.atyourservice.logger
        self._schema = None
        self.db = aysrepo.db.actor

        if template is not None:
            self._initFromTemplate(template)
        elif model is not None:
            self.model = model
        else:
            raise j.exceptions.Input(
                message="template or model needs to be specified when creating an actor", level=1, source="", tags="", msgpub="")

    @property
    def path(self):
        return j.sal.fs.joinPaths(self.aysrepo.path, "actors", self.model.name)

    def loadFromFS(self):
        """
        get content from fs and load in object
        """
        raise NotImplemented("#TODO *2")
        scode = self.model.actionsSourceCode  # @TODO *1 is also wrong, need to check

        self.model.save()

    def saveToFS(self):
        j.sal.fs.createDir(self.path)

        path = j.sal.fs.joinPaths(self.path, "actor.json")
        j.sal.fs.writeFile(filename=path, contents=str(self.model.dictJson), append=False)

        actionspath = j.sal.fs.joinPaths(self.path, "actions.py")
        j.sal.fs.writeFile(actionspath, self.model.actionsSourceCode)

        path3 = j.sal.fs.joinPaths(self.path, "config.json")
        if self.model.data != {}:
            j.sal.fs.writeFile(path3, self.model.dataJSON)

        path4 = j.sal.fs.joinPaths(self.path, "schema.capnp")
        if self.model.dbobj.serviceDataSchema.strip() != "":
            j.sal.fs.writeFile(path4, self.model.dbobj.serviceDataSchema)

    def saveAll(self):
        self.model.save()
        self.saveToFS()

    def _initFromTemplate(self, template):
        self.model = self.db.new()

        self.model.dbobj.name = template.name

        self.model.dbobj.state = "new"

        # hrd schema to capnp
        if self.model.dbobj.serviceDataSchema != template.schemaCapnpText:
            self.processChange("dataschema")
            self.model.dbobj.serviceDataSchema = template.schemaCapnpText

        if self.model.dbobj.dataUI != template.dataUI:
            self.processChange("ui")
            self.model.dbobj.dataUI = template.dataUI

        if self.model.dataJSON != template.configJSON:
            self.processChange("config")
            self.model.dbobj.data = msgpack.dumps(template.configDict)

        # git location of actor
        self.model.dbobj.gitRepo.url = self.aysrepo.git.remoteUrl
        actorpath = j.sal.fs.joinPaths(self.aysrepo.path, "actors", self.model.name)
        self.model.dbobj.gitRepo.path = j.sal.fs.pathRemoveDirPart(self.path, actorpath)

        # process origin,where does the template come from
        # TODO: *1 need to check if template can come from other aysrepo than the one we work on right now
        self.model.dbobj.origin.gitUrl = template.aysrepo.git.remoteUrl
        self.model.dbobj.origin.path = template.pathRelative

        if template.parentActor is not None:
            parentobj = template.parentActor
            self.model.dbobj.parent.actorName = parentobj.model.name
            self.model.dbobj.parent.actorKey = parentobj.model.key
            self.model.dbobj.parent.minServices = 1
            self.model.dbobj.parent.maxServices = 1

        for i, producer in enumerate(template.producers):
            self.model.dbobj.init('producers', len(template.producers))
            prod = self.model.dbobj.producers[i]
            prod.actorName = producer.model.name
            prod.actorKey = producer.model.key
            prod.minServices = producer.model.minServices
            prod.maxServices = producer.model.maxServices

        #
        # producers_schema_info = actor.schemaServiceHRD.consumeSchemaItemsGet()
        # if producers_schema_info != []:
        #     for producer_schema_info in producers_schema_info:
        #
        #         producer_role = producer_schema_info.consume_link
        #         if producer_role in args:
        #             # instance name of the comusmption is specified
        #             instance = args[producer_role]
        #         else:
        #             instance = ''
        #
        #         res = self.aysrepo.db.service.find(name=instance, actor="%s.*" % producer_role)
        #         producer_obj = None
        #         if len(res) > 1:
        #             raise j.exceptions.Input(message="found more than 1 producer:%s!%s for %s" % (
        #                                      producer_role, instance, self), level=1, source="", tags="", msgpub="")
        #
        #         elif len(res) <= 0:
        #             if producer_schema_info.auto is True:  # auto creation of the producer is enabled
        #                 actor = self.aysrepo.actorGet(producer_role, reload=False)
        #                 producer_obj = actor.serviceCreate(instance='auto', args={})
        #             else:
        #                 raise j.exceptions.Input(message="could not find producer:%s!%s for %s" % (
        #                                          producer_role, instance, self), level=1, source="", tags="", msgpub="")
        #
        #         if producer_obj is None:
        #             producer_obj = res[0].objectGet(self.aysrepo)
        #         self.model.producerAdd(producer_obj.actor.name, producer_obj.name, producer_obj.key)

        self._processActionsFile(template=template)

        self.saveToFS()

    def _processActionsFile(self, template):
        self._out = ""

        actionmethodsRequired = ["input", "init", "install", "stop", "start", "monitor", "halt", "check_up", "check_down",
                                 "check_requirements", "cleanup", "data_export", "data_import", "uninstall", "removedata", "consume"]

        actorMethods = ["input", "build"]

        actionspath = j.sal.fs.joinPaths(template.path, "actions.py")
        if j.sal.fs.exists(actionspath):
            content = j.sal.fs.fileGetContents(actionspath)
        else:
            content = "class Actions(ActionsBase):\n\n"

        if content.find("class action(ActionMethodDecorator)") != -1:
            raise j.exceptions.Input("There should be no decorator specified in %s" % self.path_actions)

        content = content.replace("from JumpScale import j", "")
        content = "from JumpScale import j\n\n%s" % content

        state = "INIT"
        amSource = ""
        amName = ""
        amDoc = ""
        amDecorator = ""
        amMethodArgs = {}

        # DO NOT CHANGE TO USE PYTHON PARSING UTILS
        lines = content.splitlines()
        for line in lines:
            linestrip = line.strip()
            if state == "INIT" and linestrip.startswith("class Actions"):
                state = "MAIN"
                continue

            if state in ["MAIN", "INIT"]:
                if linestrip == "" or linestrip[0] == "#":
                    continue

            if state == "DEF" and (linestrip.startswith("@") or linestrip.startswith("def")):
                # means we are at end of def to new one
                self._addAction(amName, amSource, amDecorator, amMethodArgs, amDoc)
                amSource = ""
                amName = ""
                amDoc = ""
                amDecorator = ""
                amMethodArgs = {}
                state = 'MAIN'

            if state in ["MAIN", "DEF"] and linestrip.startswith("@"):
                amDecorator = linestrip
                continue

            if state == "MAIN" and linestrip.startswith("def"):
                definition, args = linestrip.split("(", 1)
                amDoc = ""
                amSource = ""
                amMethodArgs = args.rstrip('):')
                amName = definition[4:].strip()
                self.logger.debug('amName: %s' % amName)
                if amDecorator == "":
                    if amName in actorMethods:
                        amDecorator = "@actor"
                    else:
                        amDecorator = "@service"
                state = "DEF"
                continue

            if state == "DEF" and line.strip() == "":
                continue

            if state == "DEF" and line[8:12] in ["'''", "\"\"\""]:
                state = "DEFDOC"
                amDoc = ""
                continue

            if state == "DEFDOC" and line[8:12] in ["'''", "\"\"\""]:
                state = "DEF"
                continue

            if state == "DEFDOC":
                amDoc += "%s\n" % line[8:]
                continue

            if state == "DEF":
                if linestrip != line[8:].strip():
                    # means we were not rightfully intented
                    raise j.exceptions.Input(message="error in source of action from %s (indentation):\nline:%s\n%s" % (self, line, content), level=1, source="", tags="", msgpub="")
                amSource += "%s\n" % line[8:]

        # process the last one
        if amName != "":
            self._addAction(amName, amSource, amDecorator, amMethodArgs, amDoc)

        for actionname in actionmethodsRequired:
            if actionname not in self.model.actionsSortedList:
                # self.addAction(name=actionname, isDefaultMethod=True)
                # not found
                if actionname == "input":
                    amSource = "return {}"
                    self._addAction(amName="input", amSource=amSource, amDecorator="actor",
                                    amMethodArgs="self,job", amDoc="")
                else:
                    self._addAction(amName=actionname, amSource="", amDecorator="service",
                                    amMethodArgs="self,job", amDoc="")

    def _addAction(self, amName, amSource, amDecorator, amMethodArgs, amDoc):

        if amSource == "":
            amSource = "pass"

        amDoc = amDoc.strip()
        amSource = amSource.strip(" \n")

        ac = j.core.jobcontroller.db.action.new()
        ac.dbobj.code = amSource
        ac.dbobj.actorName = self.model.name
        ac.dbobj.doc = amDoc
        ac.dbobj.name = amName
        ac.dbobj.args = amMethodArgs
        ac.dbobj.lastModDate = j.data.time.epoch
        ac.dbobj.origin = "actoraction:%s:%s" % (self.model.dbobj.name, amName)

        if not j.core.jobcontroller.db.action.exists(ac.key):
            # will save in DB
            ac.save()
        else:
            ac = j.core.jobcontroller.db.action.get(key=ac.key)

        oldaction = self.model.actionGet(amName)
        if oldaction is None:
            self.processChange("action_new_%s" % amName)
            self.model.actionAdd(amName, actionKey=ac.key)
        elif oldaction.actionKey != ac.key:
            # is a mod, need to remember the new key
            self.processChange("action_mod_%s" % amName)
            oldaction.actionKey = ac.key

    def processChange(self, changeCategory):
        """template action change e.g. action_install"""
        # TODO: implement change mgmt
        pass

# SERVICE

    def serviceCreate(self, instance="main", args={}):
        """
        """

        instance = instance.lower()

        service = self.aysrepo.serviceGet(role=self.model.role, instance=instance, die=False)

        if service is not None:
            # print("NEWINSTANCE: Service instance %s!%s  exists." % (self.name, instance))
            return service
        else:
            service = Service(aysrepo=self.aysrepo, actor=self, name=instance, args=args)

        return service

    @property
    def services(self):
        """
        return a list of instance name for this template
        """
        return self.aysrepo.servicesFind(actor=self.model.dbobj.name)


# GENERIC
    # def upload2AYSfs(self, path):
    #     """
    #     tell the ays filesystem about this directory which will be uploaded to ays filesystem
    #     """
    #     j.tools.sandboxer.dedupe(
    #         path, storpath="/tmp/aysfs", name="md", reset=False, append=True)

    def __repr__(self):
        return "actor: %-15s" % (self.model.name)

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
