
from JumpScale import j

base = j.data.capnp.getModelBaseClass()


class UserModel(base):
    """
    Model Class for an user object
    """

    def index(self):
        self.collection.add2index(**self.to_dict())

    def gogsRefSet(self, name, id):
        return j.clients.gogs._gogsRefSet(self, name, id)

    def gogsRefExist(self, name):
        return j.clients.gogs._gogsRefExist(self, name)

    def _pre_save(self):
        pass
