
from JumpScale import j

base = j.data.capnp.getModelBaseClass()


class UserModel(base):
    """
    Model Class for an Issue object
    """


    def index(self):
        # put indexes in db as specified
        ind = "%s:%s:%s:%s:%s" % (self.dbobj.name.lower(), self.dbobj.fullname.lower(), self.dbobj.email,
                                  self.dbobj.id, self.dbobj.source.lower())

        self._index.index({ind: self.key})
        self._index.lookupSet("user_id", self.dbobj.id, self.key)


    def _pre_save(self):
        pass
