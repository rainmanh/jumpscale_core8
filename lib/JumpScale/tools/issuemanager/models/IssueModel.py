
from JumpScale import j

base = j.data.capnp.getModelBaseClass()


class IssueModel(base):
    """
    Model Class for an Issue object
    """

    def index(self):
        gogsRefs = ",".join(["%s_%s" % (item.name.lower(), item.id) for item in self.dbobj.gogsRefs])
        for item in self.dbobj.gogsRefs:
            # there can be multiple gogs sources
            self._index.lookupSet("gogs_%s" % item.name, item.id, self.key)

        # put indexes in db as specified
        if self.dbobj.isClosed:
            closed = 1
        else:
            closed = 0

        comments = ",".join([str(item.id) for item in self.dbobj.comments])
        assignees = ",".join([str(item) for item in self.dbobj.assignees])
        labels = ",".join([str(item) for item in self.dbobj.labels])
        ind = "%d:%d:%d:%d:%d:%d:%s:%s:%s:%s:%s" % (self.dbobj.id, self.dbobj.milestone, self.dbobj.creationTime,
                                                    self.dbobj.modTime, closed, self.dbobj.repo, self.dbobj.title.lower(),
                                                    self.dbobj.source, comments, assignees, labels)
        self._index.index({ind: self.key})
        self._index.lookupSet("issue_id", self.dbobj.id, self.key)

    def _pre_save(self):
        pass

    def gogsRefSet(self, name, id):
        return j.clients.gogs._gogsRefSet(self, name, id)

    def gogsRefExist(self, name):
        return j.clients.gogs._gogsRefExist(self, name)
