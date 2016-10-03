import msgpack
from collections import OrderedDict
from JumpScale import j

ModelBase = j.data.capnp.getModelBaseClassWithData()


class ActorModel(ModelBase):
    """
    Model Class for an Actor object
    """

    @property
    def name(self):
        if self.dbobj.name.strip() == "":
            raise j.exceptions.Input(message="name of actor cannot be empty in model",
                                     level=1, source="", tags="", msgpub="")
        return self.dbobj.name

    @property
    def role(self):
        return self.dbobj.name.split(".")[0]

    @property
    def actionsSortedList(self):
        """
        Sorted methods of the actor
        """
        if len(self.dbobj.actions) == 0:
            return []
        keys = sorted([item.name for item in self.dbobj.actions])
        return keys

    @property
    def actionsCode(self):
        """
        return dict
            key = action name
            val = source code of the action
        """
        methods = {}
        for action in self.dbobj.actions:
            action_model = j.core.jobcontroller.db.action.get(action.actionKey)
            methods[action.name] = action_model.code
        return methods

    @classmethod
    def list(self, name="", state="", returnIndex=False):
        """
        @param name can be the full name e.g. node.ssh or a rule but then use e.g. node.*  (are regexes, so need to use .* at end)
        @param state
            new
            ok
            error
            disabled
        """
        if name == "":
            name = ".*"
        if state == "":
            state = ".*"
        regex = "%s:%s" % (name, state)
        return self._index.list(regex, returnIndex=returnIndex)

    def index(self):
        # put indexes in db as specified
        ind = "%s:%s" % (self.dbobj.name, self.dbobj.state)
        self._index.index({ind: self.key})

    @classmethod
    def find(self, name="", state=""):
        """
        @param name can be the full name e.g. node.ssh or a rule but then use e.g. node.*  (are regexes, so need to use .* at end)
        @param state
            new
            ok
            error
            disabled
        """
        res = []
        for key in self.list(name, state):
            res.append(self._modelfactory.get(key))
        return res

    def objectGet(self, aysrepo):
        """
        returns an Actor object created from this model
        """
        Actor = aysrepo.getActorClass()
        return Actor(aysrepo=aysrepo, model=self)

    def recurringTemplateAdd(self, name, period=3600, log=True):
        """
        #period in seconds
        name @0 :Text; name of action
        period @1 :UInt32;
        #if True then will keep log of what happened, otherwise only when error
        log @2 :Bool;
        """
        obj = self.recurringTemplateNewObj()
        obj.name = name
        obj.period = period
        obj.log = log
        return obj

    def recurringTemplateNewObj(self, *kwargs):
        olditems = [item.to_dict() for item in self.dbobj.recurringTemplate]
        newlist = self.dbobj.init("recurringTemplate", len(olditems) + 1)
        for i, item in enumerate(olditems):
            newlist[i] = item
        recurringTemplate = newlist[-1]
        return recurringTemplate

# actions

    @property
    def actionsSourceCode(self):
        out = ""
        for action in self.dbobj.actions:
            actionKey = action.actionKey
            actionCode = j.core.jobcontroller.db.action.get(actionKey)
            defstr = ""
            # defstr = "@%s\n" % action.type
            defstr += "def %s (%s):\n" % (actionCode.dbobj.name, actionCode.dbobj.args)
            if actionCode.dbobj.doc != "":
                defstr += "    '''\n    %s\n    '''\n" % actionCode.dbobj.doc

            if actionCode.dbobj.code == "":
                defstr += "    pass\n\n"
            else:
                if actionCode.dbobj.code != "":
                    defstr += "%s\n" % j.data.text.indent(actionCode.dbobj.code, 4)

            out += defstr
        return out

    @property
    def actions(self):
        """
        return dict of action pointer model
        key = action name
        value = action pointer model
        """
        actions = {}
        for act in self.dbobj.actions:
            actions[act.name] = act
        return actions

    def actionAdd(self, name, actionKey="", type="service"):
        """
        name @0 :Text;
        #unique key for code of action (see below)
        actionKey @1 :Text;
        type: actor,node,service
        """
        if name in ["init", "build"]:
            type = "actor"
        obj = self._actionsNewObj()
        obj.name = name
        obj.actionKey = actionKey
        obj.type = type
        self.save()
        return obj

    @property
    def actionsRecurring(self):
        """
        return dict of reccuring action pointer model
        key = action name
        value = action pointer model
        """
        actions = {}
        for act in self.dbobj.recurringActions:
            actions[act.action] = act
        return actions

    @property
    def actionsEvent(self):
        """
        return dict of event action pointer model
        key = action name
        value = action pointer model
        """
        actions = {}
        for act in self.dbobj.eventActions:
            actions[act.action] = act
        return actions

    def _actionsNewObj(self):
        olditems = [item.to_dict() for item in self.dbobj.actions]
        newlist = self.dbobj.init("actions", len(olditems) + 1)
        for i, item in enumerate(olditems):
            newlist[i] = item
        action = newlist[-1]
        return action

    def parentSet(self, role, auto):
        self.dbobj.parent.actorRole = role
        self.dbobj.parent.minServices = 1
        self.dbobj.parent.maxServices = 1
        self.dbobj.parent.auto = auto
        return self.dbobj.parent

# producers
    def producerAdd(self, name, maxServices=1, actorFQDN="", actorKey=""):
        """
        name @0 :Text;
        actorFQDN @1 :Text;
        maxServices @2 :UInt8;
        actorKey  @3 :Text;
        """
        obj = self.producerNewObj()
        obj.maxServices = maxServices
        obj.actorFQDN = actorFQDN
        obj.actorKey = actorKey
        obj.name = name
        return obj

    def _producerNewObj(self):
        olditems = [item.to_dict() for item in self.dbobj.producers]
        newlist = self.dbobj.init("producers", len(olditems) + 1)
        for i, item in enumerate(olditems):
            newlist[i] = item
        producer = newlist[-1]
        return producer

    def _pre_save(self):
        pass

    @property
    def data(self):
        # return a dict
        if self.dbobj.data == b"":
            return {}
        return msgpack.loads(self.dbobj.data, encoding='utf-8')

    @property
    def dataJSON(self):
        ddict2 = OrderedDict(self.data)
        return j.data.serializer.json.dumps(ddict2, sort_keys=True, indent=True)

    @property
    def dictFiltered(self):
        ddict = self.dbobj.to_dict()
        if "data" in ddict:
            ddict.pop("data")
        # ddict.pop("dataSchema")
        return ddict

    def __repr__(self):
        out = self.dictJson + "\n"
        if self.dbobj.data not in ["", b""]:
            out += "CONFIG:\n"
            out += self.dataJSON
        return out

    __str__ = __repr__
