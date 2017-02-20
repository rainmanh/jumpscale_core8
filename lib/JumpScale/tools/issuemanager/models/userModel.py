
from JumpScale import j

base = j.data.capnp.getModelBaseClass()


class UserModel(base):
    """
    Model Class for an Issue object
    """

    def index(self):
        # put indexes in db as specified
        gogsRefs = ",".join(["%s_%s" % (item.name.lower(), item.id) for item in self.dbobj.gogsRefs])

        ind = "%s:%s:%s:%s:%s:%s:%s" % (self.dbobj.name.lower(), self.dbobj.fullname.lower(), self.dbobj.email.lower(),
                                        self.dbobj.githubId, gogsRefs, self.dbobj.iyoId, self.dbobj.telegramId)

        self.collection._index.index({ind: self.key})

        for item in self.dbobj.gogsRefs:
            # there can be multiple gogs sources
            self.collection._index.lookupSet("gogs_%s" % item.name, item.id, self.key)

    def gogsRefSet(self, name, id):
        return j.clients.gogs._gogsRefSet(self, name, id)

    def gogsRefExist(self, name):
        return j.clients.gogs._gogsRefExist(self, name)

    def _pre_save(self):
        pass
