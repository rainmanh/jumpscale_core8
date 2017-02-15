from JumpScale import j

base = j.data.capnp.getModelBaseClassCollection()


class IssueCollection(base):
    """
    This class represent a collection of Issues
    """

    def _get_keys(self, repo=0, title='', milestone='', isClosed=None, id=0, creationTime=0, modTime=0, source="",
                  returnIndex=False,):
        """
        List all keys of issue model with specified params.

        @param repo int,, id of repo the issue belongs to.
        @param title str,, title of issue.
        @param milestone int,, milestone id set to this issue.
        @param isClosed bool,, issue is closed.
        @param id int,, issue id in db.
        @param creationTime int,, epoch of creation of issue.
        @param modTime int,, epoch of modification of issue.
        @param source str,, source of remote database.
        @param returnIndexalse bool,, return the index used.
        """
        if repo == "" or repo == 0:
            repo = ".*"
        if creationTime == "" or creationTime == 0:
            creationTime = ".*"
        if modTime == "" or modTime == 0:
            modTime = ".*"
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

        regex = "%s:%s:%s:%s:%s:%s:%s:%s" % (id, milestone, creationTime, modTime, isClosed, repo, title, source)
        return self._index.list(regex, returnIndex=returnIndex)

    def list(self, repo=0, title='', milestone=0, isClosed=None, id=0, creationTime=0, modTime=0, comment=0,
             assignee=0, label='', source=""):
        """
        List all keys of issue model with specified params.

        @param repo int,, id of repo the issue belongs to.
        @param title str,, title of issue.
        @param milestone int,, milestone id set to this issue.
        @param isClosed bool,, issue is closed.
        @param id int,, issue id in db.
        @param creationTime int,, epoch of creation of issue.
        @param modTime int,, epoch of modification of issue.
        @param source str,, source of remote database.
        @param returnIndexalse bool,, return the index used.
        """
        objcts = self.find(repo, title, milestone, isClosed, id, creationTime, modTime, comment, assignee, label,
                           source)
        keys = list()
        for objct in objcts:
            keys.append(objct.key)

        return keys

    def find(self, repo=0, title='', milestone=0, isClosed=None, id=0, creationTime=0, modTime=0, comment=0,
             assignee=0, label='', source=""):
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
        comment = int(comment)
        id = int(id)
        for key in self._get_keys(id=id, isClosed=isClosed, repo=repo, title=title, source=source):
            res.append(self.get(key))

        return self._filter(res, milestone, modTime, creationTime, comment, assignee, label)

    def _filter(self, res, milestone, modTime, creationTime, comment, assignee, label):
        if milestone:
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
                            milestoneids.append(milestone_dict.get('id'))
                            break

            for model in res[::-1]:
                milestone = model.dictFiltered.get('milestone', 0)
                if milestone not in milestoneids:
                    res.remove(model)

        if modTime:
            modTime = j.data.time.getEpochAgo(modTime)
            for model in res[::-1]:
                if modTime > model.dictFiltered.get('modTime'):
                    res.remove(model)

        if creationTime:
            creationTime = j.data.time.getEpochAgo(creationTime)
            for model in res[::-1]:
                if creationTime > model.dictFiltered.get('creationTime'):
                    res.remove(model)

        if comment:
            for model in res[::-1]:
                for comment_model in model.dictFiltered.get('comments', []):
                    if comment == comment_model['id']:
                        break
                else:
                    res.remove(model)
        if assignee:
            users = j.tools.issuemanager.getUserCollectionFromDB()
            assignee_id = users.find(name=assignee)[0].dictFiltered.get('id')
            for model in res[::-1]:
                if (assignee_id not in model.dictFiltered.get('assignees', [])) or not model.dictFiltered.get('assignees', False):
                    res.remove(model)
        if label:
            for model in res[::-1]:
                if (label not in model.dictFiltered.get('labels', [])) or not model.dictFiltered.get('labels', False):
                    res.remove(model)

        return res

    def getFromId(self, id):
        key = self._index.lookupGet("issue_id", id)
        issue_model =  self.get(key, autoCreate=True)
        if key is None:
            issue_model.dbobj.id = id
        return issue_model
