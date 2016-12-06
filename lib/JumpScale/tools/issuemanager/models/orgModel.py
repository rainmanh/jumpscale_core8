
from JumpScale import j

base = j.data.capnp.getModelBaseClass()


class OrgModel(base):
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
        import ipdb; ipdb.set_trace()
        ind = "%s:%s:%s" % (self.dbobj.name.lower(), str(self.dbobj.id),
                            self.dbobj.source.lower())
        self._index.index({ind: self.key})
        self._index.lookupSet("org_id", self.dbobj.id, self.key)

    def _pre_save(self):
        pass
