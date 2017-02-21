
from JumpScale import j

base = j.data.capnp.getModelBaseClass()


class IssueModel(base):
    """
    Model Class for an Issue object
    """

    def index(self):

        source = ""
        gogsRefs = ",".join(["%s_%s" % (item.name.lower(), item.id) for item in self.dbobj.gogsRefs])
        # for item in self.dbobj.gogsRefs:
        # there can be multiple gogs sources
        # self.collection._index.lookupSet("gogs_%s" % item.name, item.id, self.key)

        # put indexes in db as specified
        if self.dbobj.isClosed:
            closed = 1
        else:
            closed = 0

        assignees = ",".join([str(item) for item in self.dbobj.assignees])
        labels = ",".join([str(item).replace(":", ";") for item in self.dbobj.labels])

        ind = "%s:%s:%s:%s:%s:%s:%s:%s:%s" % (self.dbobj.milestone, self.dbobj.creationTime,
                                              self.dbobj.modTime, closed, self.dbobj.repo, self.dbobj.title.lower().replace(":", ";"),
                                              assignees, labels, gogsRefs)
        self.collection._index.index({ind: self.key})

    def _pre_save(self):
        pass

    def gogsRefSet(self, name, id):
        return j.clients.gogs._gogsRefSet(self, name, id)

    def gogsRefExist(self, name):
        return j.clients.gogs._gogsRefExist(self, name)

    def assigneeSet(self, key):
        """
        @param key is the unique key of the member
        """
        if key not in self.dbobj.assignees:
            self.addSubItem("assignees", key)
        self.changed = True

    def commentSet(self, comment, owner=""):
        if owner == None:
            owner = ""
        for item in self.dbobj.comments:
            if item.comment != comment:
                item.comment == comment
                self.changed = True
            if item.owner != owner:
                item.owner == owner
                self.changed = True
            return
        obj = self.collection.list_comments_constructor(comment=comment, owner=owner)
        self.addSubItem("comments", obj)
        self.changed = True
