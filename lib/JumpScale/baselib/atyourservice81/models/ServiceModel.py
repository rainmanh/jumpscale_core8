from JumpScale import j

ModelBase = j.data.capnp.getModelBaseClassWithData()


VALID_STATES = ['new', 'installing', 'ok', 'error', 'disabled', 'changed']


class ServiceModel(ModelBase):

    @property
    def role(self):
        return self.dbobj.actorName.split(".")[0]

    @property
    def parent(self):
        if self.dbobj.parent.serviceName == '' or self.dbobj.parent.actorName == '':
            return None

        parentModels = self.find(name=self.dbobj.parent.serviceName, actor=self.dbobj.parent.actorName)
        if len(parentModels) <= 0:
            return None
        elif len(parentModels) > 1:
            raise j.exceptions.RuntimeError("More then one parent model found for model %s:%s" % (self.dbobj.actorName, self.dbobj.name))

        return parentModels[0]

    @property
    def producers(self):
        producers = []
        for prod in self.dbobj.producers:
            producers.extend(self.find(name=prod.serviceName, actor=prod.actorName))
        return producers

    @property
    def actions(self):
        """
        return dict
            key = action name
            val = action model
        """
        actions = {}
        for action in self.dbobj.actions:
            actions[action.name] = action
        return actions

    @property
    def actionsState(self):
        """
        return dict
            key = action name
            val = state
        state = 'new', 'installing', 'ok', 'error', 'disabled', 'changed'
        """
        actions = {}
        for action in self.dbobj.actions:
            actions[action.name] = action.state.__str__()
        return actions

    @property
    def actionsCode(self):
        """
        return dict
            key = action name
            val = source code of the action
        """
        actions = {}
        for action in self.dbobj.actions:
            action_model = j.core.jobcontroller.db.action.get(action.actionKey)
            actions[action.name] = action_model.code
        return actions

    @property
    def actionsRecurring(self):
        """
        return dict
            key = action name
            val = recurring model
        """
        recurrings = {}
        for recurring in self.dbobj.recurringActions:
            recurrings[recurring.action] = recurring
        return recurrings

    @property
    def actionsEvent(self):
        """
        return dict
            key = action name
            val = event model
        """
        events = {}
        for event in self.dbobj.eventActions:
            events[event.action] = event
        return events

    @classmethod
    def list(self, name="", actor="", state="", parent="", producer="", returnIndex=False):
        """
        @param name can be the full name e.g. myappserver or a prefix but then use e.g. myapp.*
        @param actor can be the full name e.g. node.ssh or role e.g. node.* (but then need to use the .* extension, which will match roles)
        @param parent is in form $actorName!$instance
        @param producer is in form $actorName!$instance

        @param state:
            new
            installing
            ok
            error
            disabled
            changed

        """
        if name == "":
            name = ".*"
        if actor == "":
            actor = ".*"
        if state == "":
            state = ".*"

        if parent == "":
            parent = ".*"
        elif parent.find("!") == -1:
            raise j.exceptions.Input(message="parent needs to be in format: $actorName!$instance",
                                     level=1, source="", tags="", msgpub="")
        if producer == "":
            producer = ".*"
        elif producer.find("!") == -1:
            raise j.exceptions.Input(message="producer needs to be in format: $actorName!$instance",
                                     level=1, source="", tags="", msgpub="")
        regex = "%s:%s:%s:%s:%s" % (name, actor, state, parent, producer)
        return self._index.list(regex, returnIndex=returnIndex)

    def index(self):
        # put indexes in db as specified
        if self.dbobj.parent.actorName != "":
            parent = "%s!%s" % (self.dbobj.parent.actorName, self.dbobj.parent.serviceName)
        else:
            parent = ""

        if len(self.dbobj.producers) == 0:
            ind = "%s:%s:%s:%s:%s" % (self.dbobj.name, self.dbobj.actorName, self.dbobj.state, parent, "")
            self._index.index({ind: self.key})
        else:
            # now batch all producers as more than 1 index
            #@TODO: *1 test
            index = {}
            for producer in self.dbobj.producers:
                producer2 = "%s!%s" % (producer.actorName, producer.serviceName)
                ind = "%s:%s:%s:%s:%s" % (self.dbobj.name, self.dbobj.actorName, self.dbobj.state, parent, producer2)
                index[ind] = self.key
            self._index.index(index)

    @classmethod
    def find(self, name="", actor="", state="", parent="", producer=""):
        """
        @param name can be the full name e.g. myappserver or a prefix but then use e.g. myapp.*
        @param actor can be the full name e.g. node.ssh or role e.g. node.* (but then need to use the .* extension, which will match roles)
        @param parent is in form $actorName!$instance
        @param producer is in form $actorName!$instance

        @param state:
            new
            installing
            ok
            error
            disabled
            changed

        """
        res = []
        for key in self.list(name, actor, state, producer=producer, parent=parent):
            res.append(self._modelfactory.get(key))
        return res

    def objectGet(self, aysrepo):
        """
        returns an Service object created from this model
        """
        actor = aysrepo.actorGet(self.dbobj.actorName, die=True)
        Service = aysrepo.getServiceClass()
        return Service(name=self.dbobj.name, aysrepo=aysrepo, model=self)

    def _producerNewObj(self):
        olditems = [item.to_dict() for item in self.dbobj.producers]
        newlist = self.dbobj.init("producers", len(olditems) + 1)
        for i, item in enumerate(olditems):
            newlist[i] = item
        return newlist[-1]

    def _actionsNewObj(self):
        olditems = [item.to_dict() for item in self.dbobj.actions]
        newlist = self.dbobj.init("actions", len(olditems) + 1)
        for i, item in enumerate(olditems):
            newlist[i] = item
        return newlist[-1]

    def _getActionModel(self, name):
        for action in self.dbobj.actions:
            if action.name == name:
                return action
        raise j.exceptions.NotFound("Can't find method with name %s" % name)

    def _recurringNewObj(self):
        olditems = [item.to_dict() for item in self.dbobj.recurring]
        newlist = self.dbobj.init("recurring", len(olditems) + 1)
        for i, item in enumerate(olditems):
            newlist[i] = item
        return newlist[-1]

    def _getRecurringModel(self, action_name):
        for recurring in self.dbobj.recurring:
            if recurring.action == action_name:
                return recurring
        raise j.exceptions.NotFound("Can't find recurring with name %s" % action_name)

    def _gitRepoNowObj(self):
        olditems = [item.to_dict() for item in self.dbobj.gitRepos]
        newlist = self.dbobj.init("gitRepos", len(olditems) + 1)
        for i, item in enumerate(olditems):
            newlist[i] = item
        return newlist[-1]

    @property
    def wiki(self):
        # TODO: *3
        raise NotImplemented
        out = "## service:%s state" % self.service.key

        if self.parent != "":
            out += "\n- parent:%s\n\n" % self.parent

        if self.producers != {}:
            out = "### producers\n\n"
            out += "| %-20s | %-30s |\n" % ("role", "producer")
            out += "| %-20s | %-30s |\n" % ("---", "---")
            for role, producers in self.producers.items():
                for producer in producers:
                    out += "| %-20s | %-30s |\n" % (role, producer)
            out += "\n"

        if self.recurring != {} or self.methods != {}:
            methods = OrderedDict()
            for actionname, actionstate in self.methods.items():
                methods[actionname] = [actionstate, "", 0]
            for actionname, obj in self.recurring.items():
                period, last = obj
                actionstate, _, _ = methods[actionname]
                methods[actionname] = [actionstate, period, int(last)]

            out = "### actions\n\n"
            out += "| %-20s | %-10s | %-10s | %-30s |\n" % (
                "name", "state", "period", "last")
            out += "| %-20s | %-10s | %-10s | %-30s |\n" % (
                "---", "---", "---", "---")
            for actionname, obj in methods.items():
                actionstate, period, last = obj
                out += "| %-20s | %-10s | %-10s | %-30s |\n" % (
                    actionname, actionstate, period, last)
            out += "\n"

        return out

    @property
    def dictFiltered(self):
        ddict = self.dbobj.to_dict()
        if "data" in ddict:
            ddict.pop("data")
        if "dataSchema" in ddict:
            ddict.pop("dataSchema")
        return ddict

    def actionAdd(self, key, name):
        action_obj = self._actionsNewObj()
        action_obj.state = "new"
        action_obj.actionKey = key
        action_obj.name = name
        self.save()
        return action_obj

    def producerAdd(self, actorName, serviceName, key):
        p = self._producerNewObj()
        p.actorName = actorName
        p.serviceName = serviceName
        p.key = key
        self.save()

    def recurringAdd(self, name, period):
        """
        """
        r = self._recurringAdd()
        raise NotImplemented
        name = name.lower()
        try:
            recurring = self._getRecurringModel(name)
        except j.exceptions.NotFound as e:
            recurring = self.recurringAdd()
            recurring.action = name
            recurring.lastRun = 0

        if recurring.period != period:
            recurring.period = period
            self.changed = True

    def recurringRemove(self, name):
        raise NotImplementedError
        # if name in self._model['recurring']:
        #     del self._model['recurring'][name]
        #     self.changed = True

    def repoAdd(self, url, path):
        repo = self._gitRepoNowObj()
        repo.url = url
        repo.path = path
        self.save()

    def check(self):
        """
        walks over the recurring items and if too old will execute
        """
        j.application.break_into_jshell("DEBUG NOW check recurring")

    def _pre_save(self):
        binary = self.data.to_bytes_packed()
        self._data = None
        if binary != b'':
            self.dbobj.data = binary

    def __repr__(self):
        # TODO: *1 to put back on self.wiki
        out = self.dictJson + "\n"
        if self.dbobj.dataSchema not in ["", b""]:
            out += "SCHEMA:\n"
            out += self.dbobj.dataSchema
        if self.dbobj.data not in ["", b""]:
            out += "DATA:\n"
            out += self.dataJSON
        return out

    __str__ = __repr__
