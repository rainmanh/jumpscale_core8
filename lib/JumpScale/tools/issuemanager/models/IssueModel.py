
from JumpScale import j

base = j.data.capnp.getModelBaseClass()


class IssueModel(base):
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
        if self.dbobj.isClosed:
            closed = 1
        else:
            closed = 0
        ind = "%s:%s:%s:%s:%s:%s:%s" % (self.dbobj.repo.name.lower(), self.dbobj.title.lower(), self.dbobj.milestone.name.lower(),
                                        self.dbobj.assignee.name.lower(), closed, self.dbobj.id, self.dbobj.source)
        self._index.index({ind: self.key})
        self._index.lookupSet("issue_id", self.id, self.key)

    def _pre_save(self):
        pass
