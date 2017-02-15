
from JumpScale import j

base = j.data.capnp.getModelBaseClass()


class RepoModel(base):
    """
    Model Class for an Issue object
    """


    def index(self):
        # put indexes in db as specified
        ind = "%s:%s:%s:%s" % (self.dbobj.owner.lower(), self.dbobj.name.lower(), self.dbobj.id,
                               self.dbobj.source.lower())
        self._index.index({ind: self.key})
        self._index.lookupSet("repo_id", self.dbobj.id, self.key)

    def _pre_save(self):
        pass
