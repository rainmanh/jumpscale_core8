from JumpScale import j

base = j.data.capnp.getModelBaseClassCollection()


class RepoCollection(base):
    """
    This class represent a collection of Issues
    """

    def list(self, owner=0, name='', id=0, source="", milestone="", member="", returnIndex=False):
        """
        List all keys of repo model with specified params.

        @param owner int,, id of owner the repo belongs to.
        @param name str,, name of repo.
        @param id int,, repo id in db.
        @param source str,, source of remote database.
        @param returnIndexalse bool,, return the index used.
        """
        if owner == "" or owner == 0:
            owner = ".*"
        if name == "":
            name = ".*"
        if id == "" or id == 0:
            id = ".*"
        if source == "":
            source = ".*"
        if milestone == "":
            milestone = ".*"
        if member == "":
            member = ".*"

        regex = "%s:%s:%s:%s:%s:%s" % (owner, name, id, source, milestone, member)
        return self._index.list(regex, returnIndex=returnIndex)

    def find(self, owner=0, name='', id=0, source="", milestone="", member=""):
        """
        List all instances of repo model with specified params.

        @param owner str,, name of owner the repo belongs to.
        @param name str,, name of repo.
        @param id int,, repo id in db.
        @param milestone name,, name of milestone in repo.
        @param member str,, name of member in repo.
        @param source str,, source of remote database.
        @param returnIndexalse bool,, return the index used.
        """
        res = []
        id = int(id)
        for key in self.list(owner=owner, name=name, id=id, source=source, milestone=milestone, member=member):
            res.append(self.get(key))

        return self._filter(res, milestone, member, label)

    def getFromId(self, id):
        key = self._index.lookupGet("repo_id", id)
        repo_model = self.get(key, autoCreate=True)
        if key is None:
            repo_model.dbobj.id = id
        return repo_model
