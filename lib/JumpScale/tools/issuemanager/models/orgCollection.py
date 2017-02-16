from JumpScale import j

base = j.data.capnp.getModelBaseClassCollection()


class OrgCollection(base):
    """
    This class represent a collection of Issues
    """

    def memberAdd(self, userKey,access):
        """
        """
        obj = j.data.capnp.getMemoryObj(
            schema=self._capnp_schema.Member,
            userKey=userKey,
            access=access)

        self.dbobj.members.append(obj)
        self.save()

    # def consumerRemove(self, service):
    #     """
    #     Remove the service passed in argument from the producers list
    #     """
    #     for i, consumer in enumerate(self.dbobj.consumers):
    #         if consumer.key == service.model.key:
    #             self.dbobj.consumers.pop(i)

    def list(self, owner='', name='', id='', member='', repo='', source="", returnIndex=False):
        """
        List all keys of org model with specified params.

        @param owner int,, id of org the issue belongs to.
        @param name str,, title of issue.
        @param id int,, org id in db.
        @param source str,, source of remote database.
        @param returnIndexalse bool,, return the index used.
        """
        if owner == "":
            owner = ".*"
        else:
            users = j.tools.issuemanager.getUserCollectionFromDB()
            owner_id = users.find(name=owner)[0].dictFiltered.get('id')
            owner = ".*%s.*" % owner_id

        if repo == "":
            repo = ".*"
        else:
            repo = j.tools.issuemanager.getRepoCollectionFromDB()
            repo_id = users.find(name=repo)[0].dictFiltered.get('id')
            repo = ".*%s.*" % repo_id

        if member == "":
            member = ".*"
        else:
            users = j.tools.issuemanager.getUserCollectionFromDB()
            member_id = users.find(name=member)[0].dictFiltered.get('id')
            member = ".*%s.*" % member_id

        if name == "":
            name = ".*"
        if id == "" or id == 0:
            id = ".*"
        if source == "":
            source = ".*"

        regex = "%s:%s:%s:%s:%s:%s" % (name, str(id), source, owner, member, repo)
        return self._index.list(regex, returnIndex=returnIndex)

    def find(self, owner='', name='', id='', member='', repo='', source=""):
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
        for key in self.list(owner, name, id, member, repo, source):
            res.append(self.get(key))

        return res

    def getFromGogsId(self, gogsName, gogsId, createNew=True):
        return j.clients.gogs._getFromGogsId(self, gogsName=gogsName, gogsId=gogsId, createNew=createNew)
