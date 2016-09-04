from JumpScale import j
from JumpScale.baselib.atyourservice81.models.ModelBase import ModelBase
from collections import OrderedDict

VALID_STATES = ['new', 'installing', 'ok', 'error', 'disabled', 'changed']


class ServiceModel(ModelBase):

    @classmethod
    def list(self, name="", role="", actor="", parent="", producer="", returnIndex=False):
        """
        @parent is in form $actorName!$instance
        @producer is in form $actorName!$instance

        """
        if name == "":
            name = ".*"
        if role == "":
            role = ".*"
        if actor == "":
            actor = ".*"
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
        regex = "%s:%s:%s:%s:%s" % (name, role, actor, parent, producer)
        return self._index.list(regex, returnIndex=returnIndex)

    def index(self):
        # put indexes in db as specified
        from IPython import embed
        print("DEBUG NOW index service")
        embed()
        raise RuntimeError("stop debug here")
        ind = "%s:%s:%s:%s:%s" % (self.dbobj.name, self.dbobj.role, self.dbobj.state, parent, producer)
        self._index.index({ind: self.key})

    @classmethod
    def find(self, name="", role="", state=""):
        res = []
        for key in self.list(name, role, state):
            res.append(self._modelfactory.get(key))
        return res

    def _post_init(self):
        self.dbobj.key = j.data.idgenerator.generateGUID()

    # def _get_key(self):
    #     # return a unique key to be used in db (std the key but can be overriden)
    #     return self.dbobj.role + "!" + self.dbobj.name

    def _pre_save(self):
        pass

    def index(self, db):
        # put indexes in db as specified
        ikey = self.dbobj.role + "!" + self.dbobj.name
        db.hset("actor_%s" % self.dbobj.actorName, ikey, self.dbobj.key)

        from IPython import embed
        print("DEBUG NOW cache actor")
        embed()
        raise RuntimeError("stop debug here")

    def producersAdd(self):
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

    def recurringAdd(self):
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

# OLD METHODS:

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

    def setRecurring(self, name, period):
        """
        """
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

    def removeRecurring(self, name):
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
        raise NotImplemented
        return self._model["producers"]

    def remove_producer(self, role, instance):
        raise NotImplemented
        if role not in self.producers:
            return
        key = "%s!%s" % (role, instance)
        if key in self.producers[role]:
            self.producers[role].remove(key)
            self.changed = True
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

    @property
    def wiki(self):
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

    # def save(self):
    #     if self.changed:
    #         # self.service.logger.info ("State Changed, writen to disk.")
    #         j.data.serializer.yaml.dump(self._path, self.model)
    #         self.changed = False

    def __repr__(self):
        return str(self.wiki)

    def __str__(self):
        return self.__repr__()
