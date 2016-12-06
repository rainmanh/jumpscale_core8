from JumpScale import j

base = j.data.capnp.getModelBaseClassCollection()


class OrgCollection(base):
    """
    This class represent a collection of Issues
    """

    def list(self, owner='', name='', members=[], id=0, source="", returnIndex=False):
        """
        #TODO: *1

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

    def find(self, owner='', name='', members='', id=0, source=""):

        res = []
        for key in self.list(name=name, id=id, source=source):
            res.append(self.get(key))
        return res

    def getFromId(self, id):
        key = self._index.lookupGet("org_id", id)
        return self.get(key)
