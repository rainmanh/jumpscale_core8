
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
            self.collection._index.lookupSet("gogs_%s" % item.name, item.id, self.key)

        owners = ",".join([str(item) for item in self.dbobj.owners])
        members = ",".join([str(item.key) for item in self.dbobj.members])
        repos = ",".join([str(item) for item in self.dbobj.repos])
        ind = "%s:%s:%s:%s" % (self.dbobj.name.lower(), owners, members, repos)
        self.collection._index.index({ind: self.key})

    def memberSet(self, key, access):
        """
        @param key is the unique key of the member
        """
        member = j.clients.gogs.userCollection.get(key)

        for item in self.dbobj.members:
            if item.key == key:
                if item.access != access:
                    self.changed = True
                    item.access = access
                    item.name = member.dbobj.name
                return
        obj = self.collection.list_members_constructor(access=access, key=key, name=member.dbobj.name)
        self.addSubItem("members", obj)
        self.changed = True

    def ownerSet(self, key):
        """
        """
        if key not in self.dbobj.owners:
            self.addSubItem("owners", key)
            self.changed = True

    def repoSet(self, key):
        """
        @param key, is the unique key of the repo
        """
        repo = j.clients.gogs.repoCollection.get(key)
        for item in self.dbobj.repos:
            if item.key == key:
                if item.name != repo.dbobj.name:
                    item.name = repo.dbobj.name
                    self.changed = True
                return
        obj = self.collection.list_repos_constructor(key=key, name=repo.dbobj.name)
        self.addSubItem("repos", obj)
        self.changed = True

    def gogsRefSet(self, name, id):
        return j.clients.gogs._gogsRefSet(self, name, id)

    def gogsRefExist(self, name):
        return j.clients.gogs._gogsRefExist(self, name)
