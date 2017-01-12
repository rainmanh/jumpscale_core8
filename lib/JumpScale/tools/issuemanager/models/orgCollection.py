from JumpScale import j

base = j.data.capnp.getModelBaseClassCollection()


class OrgCollection(base):
    """
    This class represent a collection of Issues
    """

    def list(self, name='', id=0, source="", returnIndex=False):
        """
        List all keys of org model with specified params.

        @param owner int,, id of org the issue belongs to.
        @param name str,, title of issue.
        @param id int,, org id in db.
        @param source str,, source of remote database.
        @param returnIndexalse bool,, return the index used.
        """
        if name == "":
            name = ".*"
        if id == "" or id == 0:
            id = ".*"
        if source == "":
            source = ".*"

        regex = "%s:%s:%s" % (name, str(id), source)
        return self._index.list(regex, returnIndex=returnIndex)

    def find(self, owner=0, name='', id=0, member=0, repo=0, source=""):
        """
        List all instances of org model with specified params.

        @param owner int,, id of org the issue belongs to.
        @param name str,, title of issue.
        @param id int,, org id in db.
        @param repo int,, member id in db.
        @param member int,, repo id in db.
        @param source str,, source of remote database.
        """
        res = []
        id = int(id)
        for key in self.list(id=id, name=name, source=source):
            res.append(self.get(key))

        if member:
            users = j.tools.issuemanager.getUserCollectionFromDB()
            member_id = users.find(name=member)[0].dictFiltered.get('id')
            for model in res[::-1]:
                for member_model in model.dictFiltered.get('members', []):
                    if member_id == member_model['userKey']:
                        break
                else:
                    res.remove(model)
        if repo:
            repos = j.tools.issuemanager.getRepoCollectionFromDB()
            repo_id = repos.find(name=repo)[0].dictFiltered.get('id')
            for model in res[::-1]:
                if (repo_id not in model.dictFiltered.get('repos', [])) or not model.dictFiltered.get('repos', False):
                    res.remove(model)
        if owner:
            users = j.tools.issuemanager.getUserCollectionFromDB()
            owner_id = users.find(name=owner)[0].dictFiltered.get('id')
            for model in res[::-1]:
                if (owner_id not in model.dictFiltered.get('owners', [])) or not model.dictFiltered.get('owners', False):
                    res.remove(model)

        return res

    def getFromId(self, id):
        key = self._index.lookupGet("org_id", id)
        return self.get(key)
