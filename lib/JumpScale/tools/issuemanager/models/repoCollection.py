from JumpScale import j

base = j.data.capnp.getModelBaseClassCollection()


class RepoCollection(base):
    """
    This class represent a collection of Issues
    """

    def list(self, owner='', name='', milestones='', assignee='', isClosed='', id=0, source="", returnIndex=False):
        """
        #TODO: *1

        """
        if owner == "":
            owner = ".*"
        if name == "":
            name = ".*"
        if id == "" or id == 0:
            id = ".*"
        if source == "":
            source = ".*"

        regex = "%s:%s:%s:%s" % (owner, name, id, source)
        return self._index.list(regex, returnIndex=returnIndex)

    def find(self, issueId='', owner='', name='', assignee='', is_closed='', id=0, source=""):
        res = []
        for key in self.list(owner=owner, name=name, id=id, source=source):
            res.append(self.get(key))
        return res

    def getFromId(self, id):
        key = self._index.lookupGet("issue_id", id)
        return self.get(key)
