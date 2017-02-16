
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
            self._index.lookupSet("gogs_%s" % item.name, item.id, self.key)
        # put indexes in db as specified
        milestones = ",".join([item.name for item in self.dbobj.milestones])
        if self.dbobj.members != []:
            from IPython import embed
            print("DEBUG NOW 97")
            embed()
            raise RuntimeError("stop debug here")
        members = ",".join([item.name for item in self.dbobj.members])
        ind = "%s:%s:%s:%s:%s:%s" % (self.dbobj.owner.lower(), self.dbobj.name.lower(), self.dbobj.id,
                                     self.dbobj.source.lower(), milestones, members)
        self._index.index({ind: self.key})

        for item in self.dbobj.gogsRefs:
            # there can be multiple gogs sources
            self._index.lookupSet("gogs_%s" % item.name, item.id, self.key)

    def _pre_save(self):
        pass

    def gogsRefSet(self, name, id):
        return j.clients.gogs._gogsRefSet(self, name, id)

    def gogsRefExist(self, name):
        return j.clients.gogs._gogsRefExist(self, name)
