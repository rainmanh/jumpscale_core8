

from JumpScale import j

from collections import OrderedDict

# don't work with properties, this only happens when init is asked for, so no big deal for performance


class ActorTemplate():

    def __init__(self, path, gitrepo=None):

        # gitrepo is given when .git found in a parent dir

        # path is path in gitrepo or absolute path
        self.logger = j.atyourservice.logger

        if gitrepo != None:
            if j.sal.fs.exists(path=path):
                # we know its absolute
                relpath = j.sal.fs.pathRemoveDirPart(
                    path, gitrepo.git.BASEDIR, removeTrailingSlash=True)
                # path is now relative path
            else:
                relpath = path
                path = j.sal.fs.joinPaths(gitrepo.git.BASEDIR, path)
                if not j.sal.fs.exists(path=path):
                    raise j.exceptions.Input(
                        "Cannot find path for template:%s" % path)
        else:
            relpath = ""

        self.pathRelative = relpath

        self.path = path

        base = j.sal.fs.getBaseName(path)
        self.name = base

        # if aysrepo is None:
        #     # means the template comes from an ays repo
        #     self.domain = j.sal.fs.getBaseName(gitrepo.BASEDIR)
        #     if not self.domain.startswith("ays_"):
        #         raise j.exceptions.Input(
        #             "name of ays template git repo should start with ays_, now:%s" % gitrepo.BASEDIR)
        #     self.domain = self.domain[4:]
        # else:
        # self.domain = j.sal.fs.getDirName(aysrepo.path, True)

        # aysrepo = aysrepo

        self.gitrepo = gitrepo
        if gitrepo is not None:
            self.giturl = self.gitrepo.git.remoteUrl
            self.gitpath = self.gitrepo.git.BASEDIR
        else:
            self.giturl = ""
            self.gitpath = ""

    @property
    def role(self):
        return self.name.split('.')[0]

    @property
    def schemaCapnpText(self):
        """
        returns capnp schema as text
        """
        path = j.sal.fs.joinPaths(self.path, "schema.capnp")
        if j.sal.fs.exists(path):
            return j.sal.fs.fileGetContents(path)
        if self.schemaHrd.capnpSchema is not "":
            return self.schemaHrd.capnpSchema
        return ""

    @property
    def schema(self):
        try:
            return j.data.capnp.getSchemaFromText(self.schemaCapnpText, name="Args")
        except Exception as e:
            errmsg = str(e).split("stack:")[0]
            msg = "Could not load capnp schema for:%s\n" % self
            msg += "- path: %s\n" % self.path
            msg += "CapnpError:\n%s" % errmsg
            raise j.exceptions.Input(message=msg, level=1, source="ays.template", tags="", msgpub="")

    @property
    def configDict(self):
        path = j.sal.fs.joinPaths(self.path, "config.yaml")
        path2 = j.sal.fs.joinPaths(self.path, "config.json")
        if j.sal.fs.exists(path, followlinks=True):
            ddict = j.data.serializer.yaml.load(path)
        elif j.sal.fs.exists(path2, followlinks=True):
            ddict = j.data.serializer.json.load(path)
        else:
            ddict = {}

        if "events" in ddict:
            for x in range(0, len(ddict["events"])):
                ddict["events"][x] = j.data.capnp.tools.listInDictCreation(
                    ddict["events"][x], "actions")
                ddict["events"][x] = j.data.capnp.tools.listInDictCreation(
                    ddict["events"][x], "secrets")
        return ddict

    @property
    def configJSON(self):
        ddict2 = OrderedDict(self.configDict)
        return j.data.serializer.json.dumps(ddict2, sort_keys=True, indent=True)

    @property
    def configYAML(self):
        ddict2 = OrderedDict(self.configDict)
        return j.data.serializer.yaml.dumps(ddict2)

    @property
    def dataUI(self):
        path = j.sal.fs.joinPaths(self.path, "ui.py")
        if j.sal.fs.exists(path, followlinks=True):
            return j.sal.fs.fileGetContents(path)
        return ""

    @property
    def recurringConfig(self):
        if "recurring" in self.configDict:
            return self.configDict["recurring"]
        else:
            return {}

    @property
    def eventsConfig(self):
        if "events" in self.configDict:
            return self.configDict["events"]
        else:
            return {}

    @property
    def linksConfig(self):
        if "links" in self.configDict:
            return self.configDict["links"]
        else:
            return {}

    @property
    def parentConfig(self):
        if "links" in self.configDict:
            if "parent" in self.configDict["links"]:
                return self.configDict["links"]["parent"]
        else:
            return {}

    @property
    def consumptionConfig(self):
        if "links" in self.configDict:
            if "consume" in self.configDict["links"]:
                return self.configDict["links"]["consume"]
        else:
            return {}

    @property
    def flists(self):
        from IPython import embed
        print("DEBUG NOW flists")
        embed()
        raise RuntimeError("stop debug here")
        flists = self._hrd.getDictFromPrefix('flists')
        for name in list(flists.keys()):
            path = j.sal.fs.joinPaths(self.path, 'flists', name)
            if j.sal.fs.exists(path):
                flists[name]['content'] = j.sal.fs.fileGetContents(path)
            elif j.sal.fs.exists(path + '.flist'):
                flists[name]['content'] = j.sal.fs.fileGetContents(path + '.flist')
            else:
                raise j.exceptions.NotFound(
                    "flist definition in %s references a file that doesn't exists: %s" % (self, path))

        return flists

    def getActorModelObj(self, aysrepo, model=None):
        if model is None:
            model = aysrepo.db.actors.new()
            model.dbobj.name = self.name
            model.dbobj.state = "new"

        # git location of actor
        if aysrepo.gitrepo != None:
            model.dbobj.gitRepo.url = aysrepo.gitrepo.git.remoteUrl
        actorpath = j.sal.fs.joinPaths(aysrepo.path, "actors", model.name)
        model.dbobj.gitRepo.path = j.sal.fs.pathRemoveDirPart(self.path, actorpath)

        # process origin,where does the template come from
        # TODO: *1 need to check if template can come from other aysrepo than the one we work on right now
        model.dbobj.origin.gitUrl = self.gitrepo.git.remoteUrl
        model.dbobj.origin.path = self.pathRelative

        for item in self.consumptionConfig:
            model.producerAdd(**item)

        # self._initFlists(model)#TODO: *1

        model.parentSet(**self.parentConfig)

        self._processActionsFile(model, j.sal.fs.joinPaths(self.path, "actions.py"))

        self._initRecurringActions(model)

        # hrd schema to capnp
        if model.dbobj.serviceDataSchema != self.schemaCapnpText:
            model.dbobj.serviceDataSchema = self.schemaCapnpText
            self.processChange("dataschema")

        if model.dbobj.dataUI != self.dataUI:
            model.dbobj.dataUI = self.dataUI
            self.processChange("ui")

    def _initRecurringActions(self, model):
        for item in self.recurringConfig:
            from IPython import embed
            print("DEBUG NOW 8787")
            embed()
            raise RuntimeError("stop debug here")
            action_model = model.actions[action]
            action_model.period = j.data.types.duration.convertToSeconds(reccuring_info['period'])
            action_model.log = j.data.types.bool.fromString(reccuring_info['log'])

    def _initFlists(self, model):

        # TODO:*1 wrong, should just check which flists are in directory
        model.dbobj.init('flists', len(self.flists))

        for i, name in enumerate(self.flists):
            info = self.flists[name]
            flistObj = model.dbobj.flists[i]
            flistObj.name = name
            flistObj.mountpoint = info['mountpoint']
            flistObj.namespace = info['namespace']
            flistObj.mode = info['mode'].lower()
            flistObj.storeUrl = info['store_url']
            flistObj.content = info['content']

    def _processActionsFile(self, model, path):
        def string_has_triple_quotes(s):
            return "'''" in s or '"""' in s

        self._out = ""

        actionmethodsRequired = ["input", "init", "install", "stop", "start", "monitor", "halt", "check_up", "check_down",
                                 "check_requirements", "cleanup", "data_export", "data_import", "uninstall", "removedata",
                                 "consume", "action_pre_", "action_post_", "init_actions_"]

        actorMethods = ["input", "build"]
        parsedActorMethods = actionmethodsRequired[:]
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
            if linestrip.startswith("#"):  # general guard for comments in the beginning of the line
                continue
            if linestrip.startswith('"""') and len(linestrip.split('"""')) > 2:
                continue

            # if state == "INIT" and linestrip.startswith("class Actions"):
            if state == "INIT" and linestrip != '':
                state = "MAIN"
                continue

            if state in ["MAIN", "INIT"]:
                if linestrip == "" or linestrip[0] == "#":
                    continue

            if state == "DEF" and line[:7] != '    def' and (linestrip.startswith("@") or linestrip.startswith("def")):
                # means we are at end of def to new one
                parsedActorMethods.append(actionName)
                self._addAction(model, actionName, amSource, amDecorator, amMethodArgs, amDoc)
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
                canbeInDocString = True

                continue

            if state == "DEF" and line.strip() == "":
                continue

            if state == "DEF" and string_has_triple_quotes(line[4:8]) and canbeInDocString:
                state = "DEFDOC"
                amDoc = ""
                continue

            if state == "DEFDOC" and string_has_triple_quotes(line[4:8]):
                state = "DEF"
                canbeInDocString = False
                continue

            if state == "DEFDOC":
                amDoc += "%s\n" % line[4:]
                continue

            if state == "DEF":
                if not string_has_triple_quotes(linestrip):
                    canbeInDocString = False
                if linestrip != line[4:].strip():
                    # means we were not rightfully intented
                    raise j.exceptions.Input(message="error in source of action from %s (indentation):\nline:%s\n%s" % (
                        self, line, content), level=1, source="", tags="", msgpub="")
                amSource += "%s\n" % line[4:]
        # process the last one
        if actionName != "":
            parsedActorMethods.append(actionName)
            self._addAction(model, actionName, amSource, amDecorator, amMethodArgs, amDoc)

        # check for removed actions in the actor
        self._checkRemovedActions(model, parsedActorMethods)

        for actionname in actionmethodsRequired:
            if actionname not in model.actionsSortedList:
                # not found

                # check if we find the action in our default actions, if yes use that one
                if actionname in j.atyourservice.baseActions:
                    actionobj, actionmethod = j.atyourservice.baseActions[actionname]
                    self._addAction2(model, actionname, actionobj)
                else:
                    if actionname == "input":
                        amSource = "return None"
                        self._addAction(model=model, actionName="input", amSource=amSource,
                                        amDecorator="actor", amMethodArgs="job", amDoc="")
                    else:
                        self._addAction(model=model, actionName=actionname, amSource="",
                                        amDecorator="service", amMethodArgs="job", amDoc="")

    def _checkRemovedActions(self, model, parsedMethods):
        for action in model.actionsSortedList:
            if action not in parsedMethods:
                self.processChange('action_del_%s' % action)

    def _addAction(self, model, actionName, amSource, amDecorator, amMethodArgs, amDoc):

        if amSource == "":
            amSource = "pass"

        amDoc = amDoc.strip()

        # THIS COULD BE DANGEROUS !!! (despiegk)
        amSource = amSource.strip(" \n")

        ac = j.core.jobcontroller.db.actions.new()
        ac.dbobj.code = amSource
        ac.dbobj.actorName = model.name
        ac.dbobj.doc = amDoc
        ac.dbobj.name = actionName
        ac.dbobj.args = amMethodArgs
        ac.dbobj.lastModDate = j.data.time.epoch
        ac.dbobj.origin = "actoraction:%s:%s" % (model.dbobj.name, actionName)

        if not j.core.jobcontroller.db.actions.exists(ac.key):
            # will save in DB
            ac.save()
        else:
            ac = j.core.jobcontroller.db.actions.get(key=ac.key)

        self._addAction2(model, actionName, ac)

    def _addAction2(self, model, actionName, action):
        """
        @param actionName = actionName
        @param action is the action object
        """
        actionObj = model.actionSet(name=actionName, key=action.key)
        if actionObj.state == "new":
            self.processChange("action_new_%s" % actionName)
        else:
            self.processChange("action_mod_%s" % actionName)

    def processChange(self, changeCategory, args={}):
        """
        template action change
        categories :
            - dataschema
            - ui
            - config
            - action_new_actionname
            - action_mod_actionname
        """
        actor = self
        pass
        # TODO: *1 walk over all services & call process change there

    def __repr__(self):
        return "actortemplate: %-25s:%s" % (self.path, self.name)
