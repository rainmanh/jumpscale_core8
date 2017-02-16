from JumpScale import j

base = j.data.capnp.getModelBaseClassCollection()


class OrgCollection(base):
    """
    This class represent a collection of Issues
    """

    def list(self, name='', repoKey="", member="", owner="", gogsId=0, returnIndex=False):

        if name == "":
            name = ".*"
        if repoKey == "":
            repoKey = ".*"
        if member == "":
            member = ".*"
        if owner == "":
            owner = ".*"
        gogsId = int(gogsId)
        if gogsId == 0:
            gogsId = ".*"

        regex = "%s:%s:%s:%s:%s" % (name, repoKey, member, owner, gogsId)
        return self._index.list(regex, returnIndex=returnIndex)

    def find(self, name='', repoKey="", member="", owner="", gogsId=0):
        """
        """
        res = []
        for key in self._get_keys(name=name, repoKey=repoKey, member=member, owner=owner, gogsId=gogsId):
            res.append(self.get(key))
        return res

    def getFromGogsId(self, gogsName, gogsId, createNew=True):
        return j.clients.gogs._getFromGogsId(self, gogsName=gogsName, gogsId=gogsId, createNew=createNew)
