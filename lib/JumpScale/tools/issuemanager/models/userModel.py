
from JumpScale import j

base = j.data.capnp.getModelBaseClass()


class UserModel(base):
    """
    Model Class for an user object
    """

    def index(self):
        self.collection.add2index(**self.to_dict())

    def gitHostRefSet(self, name, id):
        return j.clients.gogs._gitHostRefSet(self, name, id)

    def gitHostRefExists(self, name):
        return j.clients.gogs._gitHostRefExists(self, name)

    def _pre_save(self):
        pass
