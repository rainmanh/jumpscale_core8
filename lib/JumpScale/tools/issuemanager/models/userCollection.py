from JumpScale import j

base = j.data.capnp.getModelBaseClassCollection()


class UserCollection(base):
    """
    This class represent a collection of Issues
    """

    def list(self, name='', fullname='', email='', id=0, source="", returnIndex=False):
        """
        #TODO: *1

        """
        if name == "":
            name = ".*"
        if fullname == "":
            fullname = ".*"
        if id == "" or id == 0:
            id = ".*"
        if source == "":
            source = ".*"
        if email == "":
            email = ".*"

        regex = "%s:%s:%s:%s:%s" % (name, fullname, email, str(id), source)
        return self._index.list(regex, returnIndex=returnIndex)

    def find(self, name='', fullname='', email='', id=0, source=""):

        res = []
        for key in self.list(name=name, fullname=fullname, email=email, id=id, source=source):
            res.append(self.get(key))
        return res

    def getFromId(self, id):
        key = self._index.lookupGet("issue_id", id)
        return self.get(key)
