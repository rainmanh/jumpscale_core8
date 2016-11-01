from collections import OrderedDict

import msgpack
from JumpScale import j
from JumpScale.baselib.atyourservice81.models.ActorServiceBaseModel import ActorServiceBaseModel


class ActorModel(ActorServiceBaseModel):
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
    def role(self):
        return self.dbobj.name.split(".")[0]

    def objectGet(self, aysrepo):
        """
        returns an Actor object created from this model
        """
        Actor = aysrepo.getActorClass()
        actor = Actor(aysrepo=aysrepo, model=self)
        return actor

    def parentSet(self, role, auto, optional, argKey):
        changed = False
        if role != self.dbobj.parent.actorRole:
            self.dbobj.parent.actorRole = role
            changed = True

        self.dbobj.parent.minServices = 1
        self.dbobj.parent.maxServices = 1

        if auto != self.dbobj.parent.auto:
            self.dbobj.parent.auto = auto
            changed = True

        if optional != self.dbobj.parent.optional:
            self.dbobj.parent.optional = optional
            changed = True

        if argKey != self.dbobj.parent.argKey:
            self.dbobj.parent.argKey = argKey
            changed = True

        self.changed = changed

        return changed

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
        self.changed = changed
        return obj

    @property
    def dictFiltered(self):
        ddict = self.dbobj.to_dict()
        if "data" in ddict:
            ddict.pop("data")
        return ddict

    def _pre_save(self):
        pass
