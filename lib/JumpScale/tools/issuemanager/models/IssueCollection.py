from JumpScale import j

base = j.data.capnp.getModelBaseClassCollection()


class IssueCollection(base):
    """
    This class represent a collection of Issues
    """

    def list(self,  repo='', title='', milestone='', isClosed=None, id='', creationTime='', modTime='', comment='',
             assignee='', label='', source="", returnIndex=False,):
        """
        List all keys of issue model with specified params.

        @param repo int,, id of repo the issue belongs to.
        @param title str,, title of issue.
        @param milestone int,, milestone id set to this issue.
        @param isClosed bool,, issue is closed.
        @param id int,, issue id in db.
        @param creationTime int,, epoch of creation of issue.
        @param modTime int,, epoch of modification of issue.
        @param source str,, s
        ource of remote database.
        @param returnIndexalse bool,, return the index used.
        """
        flag = False
        if modTime or creationTime:
            flag = True

        if milestone == "":
            milestone = ".*"
        else:
            milestoneids = list()
            repos = j.tools.issuemanager.getRepoCollectionFromDB()
            if repo:
                repo_models = repos.find(id=repo)
            else:
                repo_models = repos.find()
            for repo_model in repo_models:
                milestones = repo_model.dictFiltered.get('milestones', False)
                if milestones:
                    for milestone_dict in milestones:
                        if milestone == milestone_dict.get('name'):
                            milestoneids.append(int(milestone_dict.get('id')))
                            break
            milestone = "|".join(milestoneids).strip()
            milestone = ".*(%s).*" % milestone
        if assignee == "":
            assignee = ".*"
        else:
            import ipdb; ipdb.set_trace()
            users = j.tools.issuemanager.getUserCollectionFromDB()
            assignee_id = users.find(name=assignee)[0].dictFiltered.get('id')
            assignee = ".*%s.*" % assignee_id

        if comment == "":
            comment = ".*"
        else:
            comment = ".*%s.*" % comment

        if label == "":
            label = ".*"
        else:
            label = ".*%s.*" % label

        if repo == "" or repo == 0:
            repo = ".*"
        if title == "":
            title = ".*"
        if milestone == "" or milestone == 0:
            milestone = ".*"
        if isClosed is None:
            isClosed = ".*"
        elif isClosed is True:
            isClosed = '1'
        elif isClosed is False:
            isClosed = '0'
        if id == "" or id == 0:
            id = ".*"
        if source == "":
            source = ".*"
        regex = "%s:%s:%s:%s:%s:%s:%s:%s:%s:%s:%s" % (id, milestone, ".*", ".*", isClosed, repo, title, source,
                                                      comment, assignee, label)
        keys = self._index.list(regex, returnIndex=returnIndex)
        indexes = dict()
        if flag:
            for index, value in self._index.redisclient.hscan_iter('index:gogs:issue'):
                if value.decode() in keys and index not in indexes:
                    indexes[value] = index
            modTime = j.data.time.getEpochAgo(modTime) if modTime else chr(127)
            creationTime = j.data.time.getEpochAgo(creationTime) if creationTime else chr(127)
            keys = list()
            for key in indexes.keys():
                index = indexes[key].decode()
                if str(modTime) < index.split(":")[2]:
                    keys.append(key.decode())
                if str(creationTime) < index.split(":")[3]:
                    keys.append(key.decode())
        return keys

    def find(self, repo='', title='', milestone='', isClosed=None, id='', creationTime='', modTime='', comment='',
             assignee='', label='', source=""):
        """
        find all instances of issue model with specified params.

        @param repo int,, id of repo the issue belongs to.
        @param title str,, title of issue.
        @param milestone int,, milestone id set to this issue.
        @param isClosed bool,, issue is closed.
        @param id int,, issue id in db.
        @param creationTime int,, epoch of creation of issue.
        @param modTime int,, epoch of modification of issue.
        @param comment int,, id of comment in issue.
        @param assignee int,, id of assignee in issue.
        @param source str,, source of remote database.
        """
        res = []
        for key in self.list(repo, title, milestone, isClosed, id, creationTime, modTime, comment, assignee,
                             label, source):
            res.append(self.get(key))

        return res

    def getFromId(self, id):
        key = self._index.lookupGet("issue_id", id)
        issue_model = self.get(key, autoCreate=True)
        if key is None:
            issue_model.dbobj.id = id
        return issue_model

    def getFromGogsId(self, gogsName, gogsId, createNew=True):
        return j.clients.gogs._getFromGogsId(self, gogsName=gogsName, gogsId=gogsId, createNew=createNew)
