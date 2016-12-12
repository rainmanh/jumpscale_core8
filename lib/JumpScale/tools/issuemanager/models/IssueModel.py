
from JumpScale import j

base = j.data.capnp.getModelBaseClass()


class IssueModel(base):
    """
    Model Class for an Issue object
    """

    def index(self):
        # put indexes in db as specified
        #@TODO: *1 needs to be implemented
        ind = "%s:%s" % (self.dbobj.name, self.dbobj.state)
        self._index.index({ind: self.key})


# producers
    # def producerAdd(self, name, maxServices=1, actorFQDN="", actorKey=""):
    #     """
    #     name @0 :Text;
    #     actorFQDN @1 :Text;
    #     maxServices @2 :UInt8;
    #     actorKey  @3 :Text;
    #     """
    #     obj = self.producerNewObj()
    #     obj.maxServices = maxServices
    #     obj.actorFQDN = actorFQDN
    #     obj.actorKey = actorKey
    #     obj.name = name
    #     self.changed = changed
    #     return obj

    # @property
    # def dictFiltered(self):
    #     ddict = self.dbobj.to_dict()
    #     if "data" in ddict:
    #         ddict.pop("data")
    #     return ddict

    def _pre_save(self):
        pass
