
from JumpScale import j

base = j.data.capnp.getModelBaseClass()


class IssueModel(base):
    """
    Model Class for an Issue object
    """

    def index(self):
        # put indexes in db as specified
        if self.dbobj.isClosed:
            closed = 1
        else:
            closed = 0
        ind = "%d:%d:%d:%d:%d:%d:%s:%s" % (self.dbobj.id, self.dbobj.milestone, self.dbobj.creationTime,
                                           self.dbobj.modTime, closed, self.dbobj.repo,
                                           self.dbobj.title.lower(), self.dbobj.source)
        self._index.index({ind: self.key})

    def _pre_save(self):
        pass
