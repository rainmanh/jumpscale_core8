
from JumpScale import j

base = j.data.capnp.getModelBaseClass()


class OrgModel(base):
    """
    Model Class for an Issue object
    """

    def index(self):
        # put indexes in db as specified
        gogsRefs = ",".join(["%s_%s" % (item.name.lower(), item.id) for item in self.dbobj.gogsRefs])
        for item in self.dbobj.gogsRefs:
            # there can be multiple gogs sources
            self._index.lookupSet("gogs_%s" % item.name, item.id, self.key)

        members = ",".join([item.key for item in self.dbobj.members])
        owners = ",".join(self.dbobj.owners)
        repos = ",".join([item.key for item in self.dbobj.repos])

        ind = "%s:%s:%s:%s:%s" % (self.dbobj.name.lower(), repos, members, owners, gogsRefs)
        self._index.index({ind: self.key})

    def memberSet(self, key, access):
        """
        """
        member = j.clients.gogs.userCollection.get(key)

        found = False
        for item in self.members:
            if item.key == key:
                if item.access != access:
                    self.changed = True
                    item.access = access
                    item.name = member.name
                found = True
        if found == False:
            self.dbobj.members.append(
                self._capnp_schema.Member.new_message(key=key, access=access, name=member.name))
            self.changed = True

    def ownerSet(self, key):
        """
        """
        if key not in self.dbobj.owners:
            # check owner exist
            from IPython import embed
            print("DEBUG NOW check owner")
            embed()
            raise RuntimeError("stop debug here")
            self.dbobj.owners.append(key)
            self.changed = True

    def repoSet(self, key):
        """
        """
        repo = j.clients.gogs.repoCollection.get(key)
        found = False
        for item in self.repos:
            if item.key == key:
                if item.name != repo.name:
                    item.name = repo.name
                    self.changed = True
                found = True
        if found == False:
            self.dbobj.repos.append(
                self._capnp_schema.Member.new_message(key=key, name=repo.name))
            self.changed = True

    def gogsRefSet(self, name, id):
        return j.clients.gogs._gogsRefSet(self, name, id)

    def gogsRefExist(self, name):
        return j.clients.gogs._gogsRefExist(self, name)
