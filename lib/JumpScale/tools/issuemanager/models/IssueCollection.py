from JumpScale import j

base = j.data.capnp.getModelBaseClassCollection()


class IssueCollection(base):
    """
    This class represent a collection of Issues
    """

    def list(self, repo=0, title='', milestone='', isClosed='', id=0, creationTime=0, modTime=0, source="",
             returnIndex=False,):
        """
        List all keys of issue model with specified params.

        @param repo int,, id of repo the issue belongs to.
        @param title str,, title of issue.
        @param milestone int,, milestone id set to this issue.
        @param isClosed bool,, issue is closed.
        @param id int,, issue id in db.
        @param creationTime int,, epoch of creation of issue.
        @param modTime int,, epoch of modification of issue.
        @param source str,, source of remote database.
        @param returnIndexalse bool,, return the index used.
        """
        if repo == "" or repo == 0:
            repo = ".*"
        if creationTime == "" or creationTime == 0:
            creationTime = ".*"
        if modTime == "" or modTime == 0:
            modTime = ".*"
        if title == "":
            title = ".*"
        if milestone == "" or milestone == 0:
            milestone = ".*"
        if isClosed is None:
            isClosed = ".*"
        elif isClosed is True:
            isclosed = '1'
        elif isclosed == False:
            isClosed = '0'
        if id == "" or id == 0:
            id = ".*"
        if source == "":
            source = ".*"

        regex = "%s:%s:%s:%s:%s:%s:%s:%s" % (id, milestone, creationTime, modTime, isClosed, repo, title, source)
        return self._index.list(regex, returnIndex=returnIndex)

    def find(self, repo=0, title='', milestone=0, isClosed=None, id=0, creationTime=0, modTime=0, source=""):
        """
        find all instances of issue model with specified params.

        @param repo int,, id of repo the issue belongs to.
        @param title str,, title of issue.
        @param milestone int,, milestone id set to this issue.
        @param isClosed bool,, issue is closed.
        @param id int,, issue id in db.
        @param creationTime int,, epoch of creation of issue.
        @param modTime int,, epoch of modification of issue.
        @param source str,, source of remote database.
        """
        res = []
        for key in self.list(id=id, milestone=milestone, creationTime=creationTime,
                             modTime=modTime, isClosed=isClosed,
                             repo=repo, title=title, source=source):
            res.append(self.get(key))
        return res

    def getFromId(self, id):
        key = self._index.lookupGet("issue_id", id)
        return self.get(key)
