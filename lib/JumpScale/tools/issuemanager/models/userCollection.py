from JumpScale import j

base = j.data.capnp.getModelBaseClassCollection()


class UserCollection(base):
    """
    This class represent a collection of Issues
    """

    def list(self, name='', fullname='', email='', id=0, source="", returnIndex=False):
        """
        List all keys of repo model with specified params.

        @param name str,, name of user.
        @param fullname str,, full name of the user.
        @param email str,, email of the user.
        @param id int,, repo id in db.
        @param source str,, source of remote database.
        @param returnIndexalse bool,, return the index used.
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
        """
        List all instances of repo model with specified params.

        @param name str,, name of user.
        @param fullname str,, full name of the user.
        @param email str,, email of the user.
        @param id int,, repo id in db.
        @param source str,, source of remote database.
        @param returnIndexalse bool,, return the index used.
        """
        res = []
        id = int(id)
        for key in self.list(name=name, fullname=fullname, email=email, id=id, source=source):
            res.append(self.get(key))
        return res

    def getFromId(self, id):
        key = self._index.lookupGet("issue_id", id)
        return self.get(key)
