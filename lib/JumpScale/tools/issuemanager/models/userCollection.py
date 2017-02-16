from JumpScale import j

base = j.data.capnp.getModelBaseClassCollection()


class UserCollection(base):
    """
    This class represent a collection of Issues
    """

    def list(self, name='', fullname='', email='', githubId=0, gogsId=0, iyoId="", telegramId="", returnIndex=False):
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
        if email == "":
            email = ".*"
        if githubId == 0 or githubId == "":
            githubId = ".*"
        gogsId = int(gogsId)
        if gogsId == 0:
            gogsId = ".*"
        if iyoId == "":
            iyoId = ".*"
        if telegramId == "":
            telegramId = ".*"

        regex = "%s:%s:%s:%s:%s:%s:%s" % (name, fullname, email, githubId, gogsId, iyoId, telegramId)
        return self._index.list(regex, returnIndex=returnIndex)

    def find(self, name='', fullname='', email='', githubId=0, gogsId=0, iyoId="", telegramId=""):
        """
        List all instances of repo model with specified params.

        @param name str,, name of user.
        @param fullname str,, full name of the user.
        @param email str,, email of the user.
        @param id int,, repo id in db.
        @param source str,, source of remote database.
        """
        res = []
        for key in self.list(name=name, fullname=fullname, email=email, githubId=githubId, gogsId=gogsId,
                             iyoId=iyoId, telegramId=telegramId):
            res.append(self.get(key))
        return res

    def getFromGogsId(self, gogsName, gogsId, createNew=True):
        return j.clients.gogs._getFromGogsId(self, gogsName=gogsName, gogsId=gogsId, createNew=createNew)
