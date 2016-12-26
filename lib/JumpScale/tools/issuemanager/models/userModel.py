
from JumpScale import j

base = j.data.capnp.getModelBaseClass()


class UserModel(base):
    """
    Model Class for an Issue object
    """

    @property
    def key(self):
        if self._key == "":
            self._key = j.data.hash.md5_string(self.dictJson)
        return self._key

    def index(self):
        # put indexes in db as specified
        ind = "%s:%s:%s:%s:%s" % (self.dbobj.name.lower(), self.dbobj.fullname.lower(), self.dbobj.email,
                                  self.dbobj.id, self.dbobj.source.lower())
        self._index.index({ind: self.key})

    def _pre_save(self):
        pass
