
from JumpScale import j

base = j.data.capnp.getModelBaseClass()


class RepoModel(base):
    """
    Model Class for a repo object
    """

    def index(self):
        self.collection.add2index(**self.to_dict())

    def gogsRefSet(self, name, id, url):
        return j.clients.gogs._gogsRefSet(self, name, id, url)

    def gogsRefExist(self, name, url):
        return j.clients.gogs._gogsRefExist(self, name, url)
