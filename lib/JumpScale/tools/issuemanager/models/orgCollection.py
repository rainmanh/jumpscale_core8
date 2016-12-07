from JumpScale import j

base = j.data.capnp.getModelBaseClassCollection()


class OrgCollection(base):
    """
    This class represent a collection of Issues
    """

    def list(self, owner=0, name='', id=0, source="", returnIndex=False):
        """
        List all keys of org model with specified params.

        @param owner int,, id of org the issue belongs to.
        @param name str,, title of issue.
        @param id int,, org id in db.
        @param source str,, source of remote database.
        @param returnIndexalse bool,, return the index used.
        """
        if name == "":
            name = ".*"
        if id == "" or id == 0:
            id = ".*"
        if source == "":
            source = ".*"

        regex = "%s:%s:%s" % (name, str(id), source)
        import ipdb; ipdb.set_trace()
        return self._index.list(regex, returnIndex=returnIndex)

    def find(self, owner=0, name='', id=0, source=""):
        """
        List all instances of org model with specified params.

        @param owner int,, id of org the issue belongs to.
        @param name str,, title of issue.
        @param id int,, org id in db.
        @param source str,, source of remote database.
        """
        res = []
        for key in self.list(name=name, id=id, source=source):
            res.append(self.get(key))
        return res

    def getFromId(self, id):
        key = self._index.lookupGet("org_id", id)
        return self.get(key)
