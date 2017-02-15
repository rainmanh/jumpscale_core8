from JumpScale import j

base = j.data.capnp.getModelBaseClassCollection()


class RepoCollection(base):
    """
    This class represent a collection of Issues
    """

    def _get_keys(self, owner=0, name='', id=0, source="", returnIndex=False):
        """
        List all keys of repo model with specified params.

        @param owner int,, id of owner the repo belongs to.
        @param name str,, name of repo.
        @param id int,, repo id in db.
        @param source str,, source of remote database.
        @param returnIndexalse bool,, return the index used.
        """
        if owner == "" or owner == 0:
            owner = ".*"
        if name == "":
            name = ".*"
        if id == "" or id == 0:
            id = ".*"
        if source == "":
            source = ".*"

        regex = "%s:%s:%s:%s" % (owner, name, id, source)
        return self._index.list(regex, returnIndex=returnIndex)

    def list(self, owner='', name='', id=0, milestone=0, member=0, label='', source=""):
        """
        List all keys of repo model with specified params.

        @param owner int,, id of owner the repo belongs to.
        @param name str,, name of repo.
        @param id int,, repo id in db.
        @param source str,, source of remote database.
        @param)
        """
        objcts = self.find(owner, name, id, milestone, member, label, source)
        keys = list()
        for objct in objcts:
            keys.append(objct.key)

        return keys

    def find(self, owner='', name='', id=0, milestone=0, member=0, label='', source=""):
        """
        List all instances of repo model with specified params.

        @param owner str,, name of owner the repo belongs to.
        @param name str,, name of repo.
        @param id int,, repo id in db.
        @param milestone name,, name of milestone in repo.
        @param member str,, name of member in repo.
        @param source str,, source of remote database.
        @param returnIndexalse bool,, return the index used.
        """
        res = []
        id = int(id)
        for key in self._get_keys(owner=owner, name=name, id=id, source=source):
            res.append(self.get(key))

        return self._filter(res, milestone, member, label)

    def _filter(self, res, milestone, member, label):
        if milestone:
            for model in res[::-1]:
                for milestone_model in model.dictFiltered.get('milestones', []):
                    if milestone == milestone_model['name']:
                        break
                else:
                    res.remove(model)

        if member:
            users = j.tools.issuemanager.getUserCollectionFromDB()
            member_id = users.find(name=member)[0].dictFiltered.get('id')
            for model in res[::-1]:
                for member_model in model.dictFiltered.get('members', []):
                    if member_id == member_model['userKey']:
                        break
                else:
                    res.remove(model)

        if label:
            for model in res[::-1]:
                if (label not in model.dictFiltered.get('labels', [])) or not model.dictFiltered.get('labels', False):
                    res.remove(model)

        return res

    def getFromId(self, id):
        key = self._index.lookupGet("repo_id", id)
        repo_model =  self.get(key, autoCreate=True)
        if key is None:
            repo_model.dbobj.id = id
        return repo_model
