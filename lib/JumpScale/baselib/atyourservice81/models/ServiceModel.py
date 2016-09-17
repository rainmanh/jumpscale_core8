from JumpScale import j
from JumpScale.baselib.atyourservice81.models.ModelBase import ModelBaseWitData


VALID_STATES = ['new', 'installing', 'ok', 'error', 'disabled', 'changed']


class ServiceModel(ModelBaseWitData):

    @property
    def name(self):
        return self.dbobj.name

    @property
    def role(self):
        return self.dbobj.actorName.split(".")[0]

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
                producer2 = "%s!%s" % (producer.actorName, producer.name)
                ind = "%s:%s:%s:%s:%s" % (self.dbobj.name, self.dbobj.actorName, self.dbobj.state, parent, producer2)
                index[ind] = self.key
            self._index.index(index)

    def objectGet(self, aysrepo):
        actor = aysrepo.actorGet(self.dbobj.actorName, die=True)
        Service = aysrepo.getServiceClass()
        return Service(name=self.dbobj.name, actor=actor, aysrepo=aysrepo, model=self)

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

    def _producersAdd(self):
        olditems = [item.to_dict() for item in self.dbobj.producers]
        newlist = self.dbobj.init("producers", len(olditems) + 1)
        for i, item in enumerate(olditems):
            newlist[i] = item
        return newlist[-1]

    def actionsAdd(self):
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

    def _recurringAdd(self):
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

    def gitRepoAdd(self):
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

    @property
    def methods(self):
        raise NotImplemented
        """
        return dict
            key = action name
            val = state
        state = 'INIT', 'ERROR', 'OK', 'DISABLED', 'DO', 'CHANGED', 'CHANGEDHRD', 'RUNNING'
        DO means: execute the action method as fast as you can
        INIT means it has not been started yet ever
        """
        methos = {}
        for action in self.dbobj.actions:
            methos[action.name] = action.state

    @property
    def recurring(self):
        raise NotImplemented
        """
        return dict
            key = action name
            val = (period,lastrun)

        lastrun = epoch
        period = e.g. 1h, 1d, ...
        """
        recurrings = {}
        for recurring in self.dbobj.recurring:
            recurrings[recurring.name] = (recurring.period, recurring.lastRun)
        return recurrings

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

    def check(self):
        """
        walks over the recurring items and if too old will execute
        """
        j.application.break_into_jshell("DEBUG NOW check recurring")

    @property
    def parent(self):
        raise NotImplemented
        return self._model["parent"]

    @parent.setter
    def parent(self, parent):
        raise NotImplemented
        # will check if service exists
        self.service.aysrepo.getServiceFromKey(parent)
        if self._model["parent"] != parent:
            self._model["parent"] = parent
            self.consume(parent)
            self.changed = True
            self.service.reset()

    @property
    def producers(self):
        producers = []
        for prod in self.dbobj.producers:
            producers.extend(self.find(name=prod.name, actor=prod.actorName))
        return producers

    def producerAdd(self, actorName, name, key):
        p = self._producersAdd()
        p.actorName = actorName
        p.name = name
        p.key = key
        self.save()

    def consume(self, producerkey="", aysi=None):
        """
        """
        raise NotImplemented
        # will check if service exists
        if aysi is None:
            aysi = self.service.aysrepo.getServiceFromKey(producerkey)
        if aysi.role not in self._model["producers"]:
            self._model["producers"][aysi.role] = []
            self.changed = True
        if aysi.key not in self._model["producers"][aysi.role]:
            self._model["producers"][aysi.role].append(aysi.key)
            self._model["producers"][aysi.role].sort()
            self.changed = True
            self.service.reset()
