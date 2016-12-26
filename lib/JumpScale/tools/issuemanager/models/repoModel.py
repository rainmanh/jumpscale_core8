
from JumpScale import j

base = j.data.capnp.getModelBaseClass()


class RepoModel(base):
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
        ind = "%s:%s:%s:%s" % (self.dbobj.owner.lower(), self.dbobj.name.lower(), self.dbobj.id,
                               self.dbobj.source.lower())
        self._index.index({ind: self.key})

    def _pre_save(self):
        pass
