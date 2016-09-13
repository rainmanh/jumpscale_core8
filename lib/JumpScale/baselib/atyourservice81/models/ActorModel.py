from JumpScale import j

from JumpScale.baselib.atyourservice81.models.ModelBase import ModelBase


class ActorModel(ModelBase):
    """
    Model Class for an Actor object
    """

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

    @property
    def object(self):
        from IPython import embed
        print("DEBUG NOW return object e.g. ays actor object")
        embed()
        raise RuntimeError("stop debug here")

    @property
    def actionsSortedList(self):
        """
        Sorted methods of the actor
        """
        if len(self.dbobj.actions) == 0:
            return []
        keys = sorted([item.name for item in self.dbobj.actions])
        return keys

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
            actionCodeKey = action.actionCodeKey
            actionCode = self._modelfactory.repo.db.actionCode.get(actionCodeKey)
            defstr = "@%s\n" % action.type
            defstr += "def %s (" % actionCode.dbobj.name
            for arg in actionCode.dbobj.args:
                default = ""
                if arg.defval.decode().strip():
                    default = "='%s'" % arg.defval.decode()
                defstr += "%s%s, " % (arg.name, default)
            defstr = defstr.rstrip(", ")
            defstr += "):\n"

            if not actionCode.dbobj.code:
                defstr += "    pass\n\n"
            else:
                defstr += "%s\n" % actionCode.dbobj.code

            out += defstr
        return out

    def actionGet(self, name):
        for act in self.dbobj.actions:
            if act.name == name:
                return act
        return None

    def actionAdd(self, name, actionCodeKey="", type="service"):
        """
        name @0 :Text;
        #unique key for code of action (see below)
        actionCodeKey @1 :Text;
        type: actor,node,service
        """
        if name in ["init", "build"]:
            type = "actor"
        obj = self.actionsNewObj()
        obj.name = name
        obj.actionCodeKey = actionCodeKey
        obj.type = type
        return obj

    def actionsNewObj(self):
        olditems = [item.to_dict() for item in self.dbobj.actions]
        newlist = self.dbobj.init("actions", len(olditems) + 1)
        for i, item in enumerate(olditems):
            newlist[i] = item
        action = newlist[-1]
        return action

    def parentSet(self, name, actorFQDN="", actorKey=""):
        """
        name @0 :Text;
        actorFQDN :Text;
        actorKey  :Text;
        """
        obj = self.parent
        obj.maxServices = 1
        obj.actorFQDN = actorFQDN
        obj.actorKey = actorKey
        obj.name = name
        return obj

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

    def producerNewObj(self):
        olditems = [item.to_dict() for item in self.dbobj.producers]
        newlist = self.dbobj.init("producers", len(olditems) + 1)
        for i, item in enumerate(olditems):
            newlist[i] = item
        producer = newlist[-1]
        return producer

    def _pre_save(self):
        pass

    # def addMethod(self, name="", source="", isDefaultMethod=False):
    #     if source != "":
    #         if name in ["input", "init"] and source.find("$(") != -1:
    #             raise j.exceptions.Input(
    #                 "Action method:%s should not have template variable '$(...' in sourcecode for init or input method." % self)
    #
    #         guid = j.data.hash.md5_string(self.actor.name + source)
    #
    #         # if new method or new code
    #         if not j.atyourservice.db.action_code.exists(guid):
    #             # create new actionCode model
    #             action_code = j.atyourservice.db.action_code.new()
    #             action_code.model.guid = guid
    #             action_code.model.name = name
    #             action_code.model.actorName = self.actor.name
    #             action_code.model.code = source
    #             action_code.model.lastModDate = j.data.time.epoch
    #             # save action_code into db
    #             action_code.save()
    #
    #             # put pointer to actionCode to actor model
    #             action = self.actionsServicesTemplateNew()
    #             action.name = name
    #             action.actionCodeKey = guid
    #
    #             self._changes[name] = True
    #
    #             self.logger.debug('action %s added to db' % name)

    # def methodChanged(self, name):
    #     if name in self._changes:
    #         return True
    #     return False
    #
    # @property
    # def isChanged(self):
    #     for v in self._changes.values():
    #         if v is True:
    #             return True
    #     return False
    #
    # def __repr__(self):
    #     out = ""
    #     for item in self.methodslist:
    #         out += "%s\n" % item
    #     return out

    # __str__ = __repr__
