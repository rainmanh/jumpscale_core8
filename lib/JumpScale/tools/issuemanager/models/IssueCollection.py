from JumpScale import j

base = j.data.capnp.getModelBaseClassCollection()


class IssueCollection(base):
    """
    This class represent a collection of Issues
    """

    def list(self, repo='', title='', milestone='', assignee='', isClosed='', returnIndex=False, id=0, source=""):
        """
        #TODO: *1

        """
        if repo == "":
            repo = ".*"
        if title == "":
            title = ".*"
        if milestone == "":
            milestone = ".*"
        if assignee == "":
            assignee = ".*"
        if isClosed == "":
            isClosed = ".*"
        if id == "" or id == 0:
            id = ".*"
        if source == "":
            source = ".*"

        regex = "%s:%s:%s:%s:%s:%s:%s" % (repo, title, milestone, assignee, isClosed, id, source)
        return self._index.list(regex, returnIndex=returnIndex)

    def find(self, issueId='', repo='', title='', milestone='', assignee='', is_closed='', id=0, source=""):

        res = []
        for key in self.list(repo, title, milestone, assignee, is_closed, id, source):
            res.append(self.get(key))
        return res

    def getFromId(self, id):
        key = self._index.lookupGet("issue_id", id)
        return self.get(key)
