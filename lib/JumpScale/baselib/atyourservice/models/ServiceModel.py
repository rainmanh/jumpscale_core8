from JumpScale import j
from JumpScale.baselib.atyourservice.models.ModelBase import ModelBase
from collections import OrderedDict

VALID_STATES = ['new', 'installing', 'ok', 'error', 'disabled', 'changed']


class ServiceModel(ModelBase):

    def __init__(self, category='', db=None, key=''):
        self._capnp = j.atyourservice.db.AYSModel.Service
        super(ServiceModel, self).__init__(category=category, db=db, key=key)

    def _post_init(self):
        self.dbobj.key = j.data.idgenerator.generateGUID()

    def _get_key(self):
        # return a unique key to be used in db (std the key but can be overriden)
        return self.dbobj.role + "!" + self.dbobj.instance

    def _pre_save(self):
        pass

    def producersAdd(self):
        olditems = [item.to_dict() for item in self.dbobj.producers]
        newlist = self.dbobj.init("producers", len(olditems), 1)
        for i, item in enumerate(olditems):
            newlist[i] = item
        return newlist[-1]

    def actionsAdd(self):
        olditems = [item.to_dict() for item in self.dbobj.actions]
        newlist = self.dbobj.init("actions", len(olditems), 1)
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
        newlist = self.dbobj.init("recurring", len(olditems),  1)
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
        newlist = self.dbobj.init("gitRepos", len(olditems),  1)
        for i, item in enumerate(olditems):
            newlist[i] = item
        return newlist[-1]

    @property
    def methods(self):
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

    def set(self, name, state="DO"):
        """
        state = 'INIT', 'ERROR', 'OK', 'DISABLED', 'DO', 'CHANGED', 'CHANGEDHRD', 'RUNNING'
        DO means: execute the action method as fast as you can
        INIT means it has not been started yet ever
        """

        if state not in VALID_STATES:
            raise j.exceptions.Input("State needs to be in %s" % ','.join(VALID_STATES))
        name = name.lower()
        try:
            action = self._getActionModel(name)
        except j.exceptions.NotFound:
            action = self.actionsAdd()
            action.name = name

        if state != action.state:
            action.state = state
            self.changed = True

        return action

    def get(self, name, die=True):
        name = name.lower()
        try:
            return self._getActionModel(name)
        except j.exceptions.NotFound as e:
            if die:
                raise e
            else:
                return None

    # @property
    # def actor(self):
    #     return self._model["actor"]

    # @actor.setter
    # def actor(self, actor):
    #     self._model["actor"] = actor
    #     self.changed = True

    # @property
    # def instanceHRDHash(self):
    #     return self._model["instanceHRDHash"]
    #
    # @instanceHRDHash.setter
    # def instanceHRDHash(self, instanceHRDHash):
    #     self._model["instanceHRDHash"] = instanceHRDHash
    #     self.changed = True
    #
    # @property
    # def templateHRDHash(self):
    #     return self._model["templateHRDHash"]
    #
    # @templateHRDHash.setter
    # def templateHRDHash(self, templateHRDHash):
    #     self._model["templateHRDHash"] = templateHRDHash
    #     self.changed = True

    @property
    def recurring(self):
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
        # TODO if needed
        raise NotImplementedError
        # if name in self._model['recurring']:
        #     del self._model['recurring'][name]
        #     self.changed = True

    @property
    def events(self):
        """
        return dict
            key = event name
            val = [actions]
        """
        try:
            return self._model["events"]
        except KeyError:
            return {}

    def setEvents(self, event, actions):
        """
        """
        event = event.lower()
        change = False
        if event not in self._model["events"]:
            change = True
        else:
            self._model["events"][event].sort()
            actions.sort()
            if self._model["events"][event] != actions:
                change = True

        if change:
            self._model["events"][event] = actions
        self.changed = change

    def removeEvent(self, event):
        if event in self._model['events']:
            del self._model['events'][event]
            self.changed = True

    def check(self):
        """
        walks over the recurring items and if too old will execute
        """
        j.application.break_into_jshell("DEBUG NOW check recurring")

    @property
    def parent(self):
        return self._model["parent"]

    @parent.setter
    def parent(self, parent):
        # will check if service exists
        self.service.aysrepo.getServiceFromKey(parent)
        if self._model["parent"] != parent:
            self._model["parent"] = parent
            self.consume(parent)
            self.changed = True
            self.service.reset()

    @property
    def producers(self):
        return self._model["producers"]

    def remove_producer(self, role, instance):
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
    def model(self):
        return self._model

    @property
    def wiki(self):

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
