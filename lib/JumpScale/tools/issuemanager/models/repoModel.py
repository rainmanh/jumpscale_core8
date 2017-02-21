
from JumpScale import j

base = j.data.capnp.getModelBaseClass()


class RepoModel(base):
    """
    Model Class for an Issue object
    """

    def index(self):
        gogsRefs = ",".join(["%s_%s" % (item.name.lower(), item.id) for item in self.dbobj.gogsRefs])
        for item in self.dbobj.gogsRefs:
            # there can be multiple gogs sources
            self.collection._index.lookupSet("gogs_%s" % item.name, item.id, self.key)

        milestones = ",".join([str(item.name) for item in self.dbobj.milestones])
        members = ",".join([str(item.userKey) for item in self.dbobj.members])
        labels = ",".join([str(item) for item in self.dbobj.labels])
        # put indexes in db as specified
        ind = "%s:%s:%s:%s:%s:%s:%s" % (self.dbobj.owner.lower(), self.dbobj.name.lower(), self.dbobj.id,
                                        self.dbobj.source.lower(), milestones, members, labels)
        self.collection._index.index({ind: self.key})

    def _pre_save(self):
        pass

    def gogsRefSet(self, name, id):
        return j.clients.gogs._gogsRefSet(self, name, id)

    def gogsRefExist(self, name):
        return j.clients.gogs._gogsRefExist(self, name)
