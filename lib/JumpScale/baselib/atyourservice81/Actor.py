import msgpack

from JumpScale import j
from JumpScale.baselib.atyourservice81.Service import Service
import capnp
from JumpScale.baselib.atyourservice81 import model_capnp as ModelCapnp


class Actor():

    def __init__(self, aysrepo, template=None, model=None, name=None):
        """
        init from a template or from a model
        """

        self.aysrepo = aysrepo
        self.logger = j.atyourservice.logger
        self._schema = None
        self.model = None

        if template is not None:
            self._initFromTemplate(template)
        elif model is not None:
            self.model = model
        elif name is not None:
            self.loadFromFS(name)
        else:
            raise j.exceptions.Input(
                message="template or model or name needs to be specified when creating an actor", level=1, source="", tags="", msgpub="")

    @property
    def path(self):
        return j.sal.fs.joinPaths(self.aysrepo.path, "actors", self.model.name)

    def loadFromFS(self, name):
        """
        get content from fs and load in object
        """
        if self.model is None:
            self.model = self.aysrepo.db.actors.new()

        actor_path = j.sal.fs.joinPaths(self.aysrepo.path, "actors", name)
        self.logger.debug("load actor from FS: %s" % actor_path)
        json = j.data.serializer.json.load(j.sal.fs.joinPaths(actor_path, "actor.json"))

        # for now we don't reload the actions codes.
        # when using distributed DB, the actions code could still be available
        del json['actions']
        self.model.dbobj = ModelCapnp.Actor.new_message(**json)

        # need to save already here cause processActionFile is doing a find
        # and it need to be able to find this new actor model we are creating
        self.model.save()

        # recreate the actions code from the action.py file from the file system
        self._processActionsFile(j.sal.fs.joinPaths(actor_path, "actions.py"))

        self.saveAll()

    def saveToFS(self):
        j.sal.fs.createDir(self.path)

        path = j.sal.fs.joinPaths(self.path, "actor.json")
        j.sal.fs.writeFile(filename=path, contents=str(self.model.dictJson), append=False)

        actionspath = j.sal.fs.joinPaths(self.path, "actions.py")
        j.sal.fs.writeFile(actionspath, self.model.actionsSourceCode)

        # path3 = j.sal.fs.joinPaths(self.path, "config.json")
        # if self.model.data != {}:
        #     j.sal.fs.writeFile(path3, self.model.dataJSON)

        path4 = j.sal.fs.joinPaths(self.path, "schema.capnp")
        if self.model.dbobj.serviceDataSchema.strip() != "":
            j.sal.fs.writeFile(path4, self.model.dbobj.serviceDataSchema)

    def saveAll(self):
        self.model.save()
        self.saveToFS()

    def _initFromTemplate(self, template):
        if self.model is None:
            self.model = self.aysrepo.db.actors.new()
            self.model.dbobj.name = template.name
            self.model.dbobj.state = "new"

        # git location of actor
        self.model.dbobj.gitRepo.url = self.aysrepo.git.remoteUrl
        actorpath = j.sal.fs.joinPaths(self.aysrepo.path, "actors", self.model.name)
        self.model.dbobj.gitRepo.path = j.sal.fs.pathRemoveDirPart(self.path, actorpath)

        # process origin,where does the template come from
        # TODO: *1 need to check if template can come from other aysrepo than the one we work on right now
        self.model.dbobj.origin.gitUrl = template.remoteUrl
        self.model.dbobj.origin.path = template.pathRelative

        self._initParent(template)
        self._initProducers(template)
        self._initFlists(template)

        self._processActionsFile(j.sal.fs.joinPaths(template.path, "actions.py"))
        self._initRecurringActions(template)

        # hrd schema to capnp
        if self.model.dbobj.serviceDataSchema != template.schemaCapnpText:
            self.model.dbobj.serviceDataSchema = template.schemaCapnpText
            self.processChange("dataschema")

        if self.model.dbobj.dataUI != template.dataUI:
            self.model.dbobj.dataUI = template.dataUI
            self.processChange("ui")

        # if self.model.dataJSON != template.configJSON:
        #     self.model.dbobj.data = msgpack.dumps(template.configDict)
        #     self.processChange("config")

        self.saveToFS()
        self.model.save()

    def _initParent(self, template):
        parent = template.schemaHrd.parentSchemaItemGet()
        if parent is not None:
            parent_name = parent.parent
            parent_role = parent_name.split('.')[0]
            self.model.parentSet(role=parent_role, auto=bool(parent.auto), optional=bool(parent.optional), argKey=parent.name)

    def _initProducers(self, template):
        consumed_actors = template.schemaHrd.consumeSchemaItemsGet()
        self.model.dbobj.init('producers', len(consumed_actors))

        for i, consume_info in enumerate(consumed_actors):
            actor_name = consume_info.consume_link
            actor_role = actor_name.split('.')[0]

            producer = self.model.dbobj.producers[i]
            producer.actorRole = actor_role
            producer.minServices = int(consume_info.consume_nr_min)
            producer.maxServices = int(consume_info.consume_nr_max)
            producer.auto = bool(consume_info.auto)
            producer.argKey = consume_info.name

    def _initRecurringActions(self, template):
        for action, reccuring_info in template.recurringDict.items():
            action_model = self.model.actions[action]
            action_model.period = j.data.types.duration.convertToSeconds(reccuring_info['period'])
            action_model.log = j.data.types.bool.fromString(reccuring_info['log'])

    def _initFlists(self, template):
        self.model.dbobj.init('flists', len(template.flists))

        for i, name in enumerate(template.flists):
            info = template.flists[name]
            flistObj = self.model.dbobj.flists[i]
            flistObj.name = name
            flistObj.mountpoint = info['mountpoint']
            flistObj.namespace = info['namespace']
            flistObj.mode = info['mode'].lower()
            flistObj.storeUrl = info['store_url']
            flistObj.content = info['content']

    def _processActionsFile(self, path):
        self._out = ""

        actionmethodsRequired = ["input", "init", "install", "stop", "start", "monitor", "halt", "check_up", "check_down",
                                 "check_requirements", "cleanup", "data_export", "data_import", "uninstall", "removedata",
                                 "consume", "action_pre_", "action_post_", "init_actions_"]

        actorMethods = ["input", "build"]

        if j.sal.fs.exists(path):
            content = j.sal.fs.fileGetContents(path)
        else:
            content = "class Actions():\n\n"

        if content.find("class action(ActionMethodDecorator)") != -1:
            raise j.exceptions.Input("There should be no decorator specified in %s" % self.path_actions)

        content = content.replace("from JumpScale import j", "")
        content = "from JumpScale import j\n\n%s" % content

        state = "INIT"
        amSource = ""
        actionName = ""
        amDoc = ""
        amDecorator = ""
        amMethodArgs = {}

        # DO NOT CHANGE TO USE PYTHON PARSING UTILS
        lines = content.splitlines()
        for line in lines:
            linestrip = line.strip()
            # if state == "INIT" and linestrip.startswith("class Actions"):
            if state == "INIT" and linestrip != '':
                state = "MAIN"
                continue

            if state in ["MAIN", "INIT"]:
                if linestrip == "" or linestrip[0] == "#":
                    continue

            if state == "DEF" and line[:7] != '    def' and (linestrip.startswith("@") or linestrip.startswith("def")):
                # means we are at end of def to new one
                self._addAction(actionName, amSource, amDecorator, amMethodArgs, amDoc)
                amSource = ""
                actionName = ""
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
                actionName = definition[4:].strip()
                if amDecorator == "":
                    if actionName in actorMethods:
                        amDecorator = "@actor"
                    else:
                        amDecorator = "@service"
                state = "DEF"
                continue

            if state == "DEF" and line.strip() == "":
                continue

            if state == "DEF" and line[4:8] in ["'''", "\"\"\""]:
                state = "DEFDOC"
                amDoc = ""
                continue

            if state == "DEFDOC" and line[4:8] in ["'''", "\"\"\""]:
                state = "DEF"
                continue

            if state == "DEFDOC":
                amDoc += "%s\n" % line[4:]
                continue

            if state == "DEF":
                if linestrip != line[4:].strip():
                    # means we were not rightfully intented
                    raise j.exceptions.Input(message="error in source of action from %s (indentation):\nline:%s\n%s" % (
                        self, line, content), level=1, source="", tags="", msgpub="")
                amSource += "%s\n" % line[4:]

        # process the last one
        if actionName != "":
            self._addAction(actionName, amSource, amDecorator, amMethodArgs, amDoc)

        for actionname in actionmethodsRequired:
            if actionname not in self.model.actionsSortedList:
                # not found

                # check if we find the action in our default actions, if yes use that one
                if actionname in j.atyourservice.baseActions:
                    actionobj, actionmethod = j.atyourservice.baseActions[actionname]
                    self._addAction2(actionname, actionobj)
                else:
                    if actionname == "input":
                        amSource = "return None"
                        self._addAction(actionName="input", amSource=amSource,
                                        amDecorator="actor", amMethodArgs="job", amDoc="")
                    else:
                        self._addAction(actionName=actionname, amSource="",
                                        amDecorator="service", amMethodArgs="job", amDoc="")

    def _addAction(self, actionName, amSource, amDecorator, amMethodArgs, amDoc):

        if amSource == "":
            amSource = "pass"

        amDoc = amDoc.strip()

        # THIS COULD BE DANGEROUS !!! (despiegk)
        amSource = amSource.strip(" \n")

        ac = j.core.jobcontroller.db.actions.new()
        ac.dbobj.code = amSource
        ac.dbobj.actorName = self.model.name
        ac.dbobj.doc = amDoc
        ac.dbobj.name = actionName
        ac.dbobj.args = amMethodArgs
        ac.dbobj.lastModDate = j.data.time.epoch
        ac.dbobj.origin = "actoraction:%s:%s" % (self.model.dbobj.name, actionName)

        if not j.core.jobcontroller.db.actions.exists(ac.key):
            # will save in DB
            ac.save()
        else:
            ac = j.core.jobcontroller.db.actions.get(key=ac.key)

        self._addAction2(actionName, ac)

    def _addAction2(self, actionName, action):
        """
        @param actionName = actionName
        @param action is the action object
        """
        actionObj = self.model.actionAdd(name=actionName, key=action.key)
        if actionObj.state == "new":
            self.processChange("action_new_%s" % actionName)
        else:
            self.processChange("action_mod_%s" % actionName)

    def processChange(self, changeCategory):
        """
        template action change
        categories :
            - dataschema
            - ui
            - config
            - action_new_actionname
            - action_mod_actionname
        """
        # self.logger.debug('process change for %s (%s)' % (self, changeCategory))
        if changeCategory == 'dataschema':
            # TODO
            pass

        elif changeCategory == 'ui':
            # TODO
            pass

        elif changeCategory == 'config':
            # TODO
            pass

        elif changeCategory.find('action_new') != -1:
            # TODO
            pass
        elif changeCategory.find('action_mod') != -1:
            # TODO
            pass

        for service in self.aysrepo.servicesFind(actor=self.model.name):
            service.processChange(actor=self, changeCategory=changeCategory)

# SERVICE

    def serviceCreate(self, instance="main", args={}):
        instance = instance.lower()
        service = self.aysrepo.serviceGet(role=self.model.role, instance=instance, die=False)
        if service is not None:
            service._check_args(self, args)
            return service

        # checking if we have the service on the file system
        target = "%s!%s" % (self.model.name, instance)
        services_dir = j.sal.fs.joinPaths(self.aysrepo.path, 'services')
        results = j.sal.fs.walkExtended(services_dir, files=False, dirPattern=target)
        if len(results) > 1:
            raise j.exceptions.RuntimeError("found more then one service directory for %s" % target)
        elif len(results) == 1:
            service = Service(aysrepo=self.aysrepo, path=results[0])
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
    def __repr__(self):
        return "actor: %-15s" % (self.model.name)
