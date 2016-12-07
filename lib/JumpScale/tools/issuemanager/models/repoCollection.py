from JumpScale import j

base = j.data.capnp.getModelBaseClassCollection()


class RepoCollection(base):
    """
    This class represent a collection of Issues
    """

    def list(self, owner=0, name='', id=0, source="", returnIndex=False):
        """
        List all keys of repo model with specified params.

        @param owner int,, id of owner the repo belongs to.
        @param name str,, name of repo.
        @param id int,, repo id in db.
        @param source str,, source of remote database.
        @param returnIndexalse bool,, return the index used.
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

    def find(self, owner='', name='', id=0, source=""):
        """
        List all instances of repo model with specified params.

        @param owner int,, id of owner the repo belongs to.
        @param name str,, name of repo.
        @param id int,, repo id in db.
        @param source str,, source of remote database.
        @param returnIndexalse bool,, return the index used.
        """
        res = []
        for key in self.list(owner=owner, name=name, id=id, source=source):
            res.append(self.get(key))
        return res

    def getFromId(self, id):
        key = self._index.lookupGet("issue_id", id)
        return self.get(key)
