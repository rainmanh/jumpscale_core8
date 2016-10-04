from JumpScale import j
from JumpScale.baselib.atyourservice81.Service import Service

from collections import OrderedDict
import msgpack


class Actor():

    def __init__(self, aysrepo, template=None, model=None):
        """
        init from a template or from a model
        """

        self.aysrepo = aysrepo
        self.logger = j.atyourservice.logger
        self._schema = None
        self.db = aysrepo.db.actor
        self.model = None

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
        if self.model is None:
            self.model = self.db.new()
            self.model.dbobj.name = template.name
            self.model.dbobj.state = "new"

        # hrd schema to capnp
        if self.model.dbobj.serviceDataSchema != template.schemaCapnpText:
            self.model.dbobj.serviceDataSchema = template.schemaCapnpText
            self.processChange("dataschema")

        if self.model.dbobj.dataUI != template.dataUI:
            self.model.dbobj.dataUI = template.dataUI
            self.processChange("ui")

        if self.model.dataJSON != template.configJSON:
            self.model.dbobj.data = msgpack.dumps(template.configDict)
            self.processChange("config")

        # git location of actor
        self.model.dbobj.gitRepo.url = self.aysrepo.git.remoteUrl
        actorpath = j.sal.fs.joinPaths(self.aysrepo.path, "actors", self.model.name)
        self.model.dbobj.gitRepo.path = j.sal.fs.pathRemoveDirPart(self.path, actorpath)

        # process origin,where does the template come from
        # TODO: *1 need to check if template can come from other aysrepo than the one we work on right now
        self.model.dbobj.origin.gitUrl = template.aysrepo.git.remoteUrl
        self.model.dbobj.origin.path = template.pathRelative

        self._initParent(template)
        self._initProducers(template)
        self._initRecurringActions(template)
        self._initEventActions(template)

        self._processActionsFile(template=template)

        self.saveToFS()
        self.model.save()

    def _initParent(self, template):
        parent = template.schemaHrd.parentSchemaItemGet()
        if parent is not None:
            parent_name = parent.parent
            parent_role = parent_name.split('.')[0]
            self.model.parentSet(role=parent_role, auto=bool(parent.auto))

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

    def _initRecurringActions(self, template):
        self.model.dbobj.init('recurringActions', len(template.recurringDict))

        for i, action in enumerate(template.recurringDict):
            reccuring_info = template.recurringDict[action]
            recurring = self.model.dbobj.recurringActions[i]
            recurring.action = action
            recurring.period = j.data.types.duration.convertToSeconds(reccuring_info['period'])
            recurring.log = j.data.types.bool.fromString(reccuring_info['log'])

    def _initEventActions(self, template):
        # TODO format for event in hrd is ugly, need better
        self.model.dbobj.init('eventActions', len(template.eventDict))

        for i, item in enumerate(template.eventDict):
            event, action = item.split('.')
            eventObj = self.model.dbobj.eventActions[i]
            eventObj.action = action
            eventObj.event = event
            log = template.eventDict[item]['log']
            eventObj.log = j.data.types.bool.fromString(log)

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
            # if state == "INIT" and linestrip.startswith("class Actions"):
            if state == "INIT" and linestrip != '':
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
                continue

            if state in ["MAIN", "DEF"] and linestrip.startswith("@"):
                amDecorator = linestrip
                continue

            if state == "MAIN" and linestrip.startswith("def"):
                definition, args = linestrip.split("(", 1)
                amDoc = ""
                amSource = ""
                amMethodArgs = args.rstrip('):')
                amName = definition[4:].strip()
                if amDecorator == "":
                    if amName in actorMethods:
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
                    raise j.exceptions.Input(message="error in source of action from %s (indentation):\nline:%s\n%s" % (self, line, content), level=1, source="", tags="", msgpub="")
                amSource += "%s\n" % line[4:]

        # process the last one
        if amName != "":
            self._addAction(amName, amSource, amDecorator, amMethodArgs, amDoc)

        for actionname in actionmethodsRequired:
            if actionname not in self.model.actionsSortedList:
                # self.addAction(name=actionname, isDefaultMethod=True)
                # not found
                if actionname == "input":
                    amSource = "return {}"
                    self._addAction(amName="input", amSource=amSource, amDecorator="actor", amMethodArgs="job", amDoc="")
                else:
                    self._addAction(amName=actionname, amSource="", amDecorator="service", amMethodArgs="job", amDoc="")

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

        oldaction = self.model.actions.get(amName, None)
        if oldaction is None:
            self.model.actionAdd(amName, actionKey=ac.key)
            self.processChange("action_new_%s" % amName)
        elif oldaction.actionKey != ac.key:
            # is a mod, need to remember the new key
            oldaction.actionKey = ac.key
            self.processChange("action_mod_%s" % amName)

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
            return service

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
