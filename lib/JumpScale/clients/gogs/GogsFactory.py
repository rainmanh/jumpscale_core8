from GogsClient import GogsClient
from JumpScale import j


class GogsFactory:

    def __init__(self):
        self.__jslocation__ = "j.clients.gogs"
        self.logger = j.logger.get("j.clients.gogs")
        self.model = None

        self.userCollection = j.tools.issuemanager.getUserCollectionFromDB()
        self.orgCollection = j.tools.issuemanager.getOrgCollectionFromDB()
        self.issueCollection = j.tools.issuemanager.getIssueCollectionFromDB()
        self.repoCollection = j.tools.issuemanager.getRepoCollectionFromDB()

        self.logger = j.logger.get("j.clients.gogs")
        self.logger.info("gogs factory initted.")
        self._labels = {}

    def destroyData(self):
        self.userCollection.destroy()
        self.orgCollection.destroy()
        self.issueCollection.destroy()
        self.repoCollection.destroy()

    def createViews(self):

        C = """
        -- create view to see all labels
        CREATE OR REPLACE VIEW issue_labels AS
        select i.id,
               i.name,
               l.name as label_name
        from issue as i
        left join issue_label as il on il.issue_id=i.id
        left join label as l on l.id=il.label_id ;

        -- create aggregated view
        CREATE OR REPLACE VIEW issue_labels_grouped AS
        SELECT
          id,
          array_to_string(array_agg(label_name), ',')
        FROM
          public.issue_labels
        GROUP BY id
        ORDER BY id;

        -- view of comments
        CREATE OR REPLACE VIEW issue_comments AS
        SELECT
          issue.id,
          '{' || comment.id || ',' || comment.poster_id || '}' || comment.content as comment
        FROM issue
        left join comment on issue.id=comment.issue_id
        ORDER by issue.id;

        -- create aggregated view for comments (returns {$commentid,$committerid}||,...)
        CREATE OR REPLACE VIEW issue_comments_grouped AS
        SELECT
          id,
          array_to_string(array_agg(comment), '||')
        FROM
          public.issue_comments
        GROUP BY id
        ORDER BY id;


        """

    def getRestClient(self, addr='https://127.0.0.1', port=3000, login='root', passwd='root', accesstoken=None):
        """
        # Getting client via accesstoken

        # Create access token in gogs

        Under user profile click your settings.
        Click Applications, from there use generate new token to create your token.

        # User Access token
        rest = j.clients.gogs.getRestClient('https://docs.greenitglobe.com', 443,
                                            accesstoken='myaccesstoken')

        # Getting client via username, password
        rest = j.clients.gogs.getRestClient('https://docs.greenitglobe.com', 443,
                                            'myusername', 'mypassword')

        """
        return GogsClient(addr=addr, port=port, login=login, passwd=passwd, accesstoken=accesstoken)

    def syncAllFromPSQL(self, gogsName):
        if self.model == None:
            raise j.exceptions.Input(message="please connect to psql first, use self.connectPSQL",
                                     level=1, source="", tags="", msgpub="")
        self.logger.info("syncAllFromPSQL")
        self.getUsersFromPSQL(gogsName=gogsName)
        self.logger.info("User synced")
        self.getOrgsFromPSQL(gogsName=gogsName)
        self.logger.info("Organizations synced")
        self.getReposFromPSQL(gogsName=gogsName)
        self.logger.info("Repositories synced")
        self.getIssuesFromPSQL(gogsName=gogsName)
        self.logger.info("Issues synced")

    def connectPSQL(self, ipaddr="127.0.0.1", port=5432, login="gogs", passwd="something", dbname="gogs"):
        """
        connects to psql & connects resulting model to self.model
        is a peewee orm enabled orm
        """
        self.model = j.clients.peewee.getModel(ipaddr=ipaddr, port=port, login=login, passwd=passwd, dbname=dbname)
        return self.model

    def getIssuesFromPSQL(self, gogsName):
        """
        Load issues from remote database into model.

        @param ipaddr str,,ip address where remote database is on.
        @param port int,, port number remote database is listening on.
        @param login str,,database login.
        @param passwd str,,database passwd.
        @param dbname str,, database name.
        """
        self.logger.info("getIssuesFromPSQL")
        if self.model == None:
            raise j.exceptions.Input(message="please connect to psql first, use self.connectPSQL",
                                     level=1, source="", tags="", msgpub="")

        if self.repoCollection.list() == []:
            # need to download
            self.getReposFromPSQL()

        model = self.model

        queryString = """
        select i.id,
               i.name,
               i.repo_id,
               i.content,
               i.milestone_id,
               i.assignee_id,
               i.num_comments,
               i.created_unix,
               i.updated_unix,
               i.is_closed,
               c.id as comment_id,
               c.content as comment_content,
               c.poster_id,
               l.name as label_name
        from issue as i
        left join comment as c on c.issue_id=i.id
        left join issue_label as il on il.issue_id=i.id
        left join label as l on l.id=il.label_id
        """
        query = model.User.raw(queryString)
        issues = {}

        for issue in query:
            if issue.id not in issues:
                issues[issue.id] = {'title': issue.name,
                                    'content': issue.content,
                                    'milestone': issue.milestone_id,
                                    'is_closed': issue.is_closed,
                                    'repo': issue.repo_id,
                                    'time_created': issue.created_unix,
                                    'time_updated': issue.updated_unix,
                                    'comments': dict(),
                                    'assignees': list(),
                                    'labels': list()
                                    }
            issue_dict = issues[issue.id]
            if issue.assignee_id and issue.assignee_id not in issue_dict['assignees']:
                issue_dict['assignees'].append(issue.assignee_id)
            if issue.label_name and issue.label_name not in issue_dict['labels']:
                issue_dict['labels'].append(issue.label_name)
            if issue.comment_id:
                issue_dict['comments'][issue.comment_id] = {'owner': issue.poster_id,
                                                            'content': issue.comment_content,
                                                            'id': issue.comment_id
                                                            }

        for id, val in issues.items():
            issue_model = self.issueCollection.getFromId(id)

            issue_model.dbobj.assignees = [user for user in val.get('assignees', [])]

            for commentid, comment in val.get('comments', {}).items():
                comment_scheme = j.data.capnp.getMemoryObj(issue_model._capnp_schema.Comment, **comment)
                issue_model.dbobj.comments.append(comment_scheme)

            issue_model.dbobj.labels = [label for label in val.get('labels', [])]

            issue_model.dbobj.id = id
            issue_model.dbobj.title = val['title']
            issue_model.dbobj.content = val['content']
            issue_model.dbobj.content = val['content']
            issue_model.dbobj.milestone = val['milestone']
            issue_model.dbobj.isClosed = val['is_closed']
            issue_model.dbobj.repo = val['repo']
            issue_model.dbobj.creationTime = val['time_created']
            issue_model.dbobj.modTime = val['time_updated']
            issue_model.dbobj.source = ''
            issue_model.save()
        else:
            del issues

    def getOrgsFromPSQL(self, gogsName):
        """
        Load organizations from remote database into model.

        @param ipaddr str,,ip address where remote database is on.
        @param port int,, port number remote database is listening on.
        @param login str,,database login.
        @param passwd str,,database passwd.
        @param dbname str,, database name.
        """
        self.logger.info("getOrgsFromPSQL")

        if self.model == None:
            raise j.exceptions.Input(message="please connect to psql first, use self.connectPSQL",
                                     level=1, source="", tags="", msgpub="")

        if self.userCollection.list() == []:
            # need to download
            self.getUsersFromPSQL()

        model = self.model
        queryString = """
        select org.name,
           org.full_name,
           org.id,
           org.num_repos,
           r.name as repo_name,
           r.id as repo_id,
           ou.is_owner,
           member.id as member_id,
           access.mode as member_access
        from "user" as org
        left join repository as r on org.id=r.owner_id
        left join org_user as ou on org.id=ou.org_id
        left join "user" as member on ou.uid=member.id
        left join access on member.id=access.user_id
        where org.type=1;
        """
        query = model.User.raw(queryString)

        for org in query:

            self.logger.debug(org.__dict__)

            # get organization from gogsid
            org_model = self.orgCollection.getFromGogsId(gogsName=gogsName, gogsId=org.id)

            # get member (user) from gogs id
            member_model = self.userCollection.getFromGogsId(
                gogsName=gogsName, gogsId=org.member_id, createNew=False)  # member needs to exists

            # set member on the org model
            org_model.memberSet(member_model.key, org.member_access)

            if org_model.dbobj.name != org.name:
                org_model.dbobj.name = org.name
                org_model.changed = True

            if org.description == None:
                org.description = ""
            if org.full_name != "":
                org.description = "fullname:%s\n%s" % (org.full_name, org.description)

            if org_model.dbobj.description != org.description:
                org_model.dbobj.description = org.description
                org_model.changed = True

            org_model.gogsRefSet(name=gogsName, id=org.id)

            # process the repoobj
            repo_model = self.repoCollection.getFromGogsId(gogsName=gogsName, gogsId=org.repo_id)
            if repo_model.dbobj.name != org.repo_name:
                repo_model.dbobj.name = org.repo_name
                repo_model.changed = True

            repo_model.gogsRefSet(name=gogsName, id=int(org.repo_id))  # mark info comes from gogs
            repo_model.save()

            if org_model.dbobj.nrRepos != org.num_repos:
                org_model.dbobj.nrRepos = org.num_repos

            if org.is_owner:
                org_model.ownerSet(member_model.key)

            org_model.repoSet(repo_model.key)

            org_model.save()

    def getReposFromPSQL(self, gogsName):
        """
        Load repos from remote database into model.

        @param ipaddr str,,ip address where remote database is on.
        @param port int,, port number remote database is listening on.
        @param login str,,database login.
        @param passwd str,,database passwd.
        @param dbname str,, database name.
        """
        if self.model == None:
            raise j.exceptions.Input(message="please connect to psql first, use self.connectPSQL",
                                     level=1, source="", tags="", msgpub="")

        if self.orgCollection.list() == []:
            self.getOrgsFromPSQL()

        queryString = """
        select r.id,
               r.name,
               r.owner_id,
               r.description,
               r.num_issues,
               r.num_milestones,
               member.user_id as memberid,
               a.mode,
               l.name as label_name,
               m.name as milestone_name,
               m.id as milestone_id,
               m.is_closed as milestone_is_closed,
               m.num_issues as milestone_num_issues,
               m.num_closed_issues  as milestone_num_closed_issues,
               m.deadline_unix as milestone_deadline,
               m.completeness as milestone_completeness
        from repository as r
        left join collaboration as member on r.id=member.repo_id
        left join access as a on member.user_id=a.user_id
        left join label as l on l.repo_id=r.id
        left join milestone as m on m.repo_id=r.id
        """
        query = self.model.User.raw(queryString)
        repos = {}
        for repo in query:
            if repo.id not in repos:
                repos[repo.id] = {'name': repo.name,
                                  'owner': repo.owner_id,
                                  'description': repo.description,
                                  'num_issues': repo.num_issues,
                                  'num_milestones': repo.num_milestones,
                                  'members': dict(),
                                  'milestones': dict(),
                                  'labels': list()
                                  }
            repo_dict = repos[repo.id]
            if repo.memberid:
                repo_dict['members'][repo.memberid] = repo.mode
            if repo.label_name and repo.label_name not in repo_dict['labels']:
                repo_dict['labels'].append(repo.label_name)
            if repo.milestone_id and repo.milestone_id not in repo_dict['milestones']:
                repo_dict['milestones'][repo.milestone_id] = {'name': repo.milestone_name,
                                                              'isClosed': repo.milestone_is_closed,
                                                              'nrIssues': repo.milestone_num_issues,
                                                              'nrClosedIssues': repo.milestone_num_closed_issues,
                                                              'completeness': repo.milestone_completeness,
                                                              'deadline': repo.milestone_deadline,
                                                              'id': repo.milestone_id}

        for id, val in repos.items():
            repo_model = self.repoCollection.getFromId(id)

            repo_model.dbobj.labels = [str(name) for name in val.get('labels', [])]

            # if val['members']:
            #     repo_model.dbobj.init('members', len(val['members']))
            repo_model.dbobj.members = []
            for memberid, member in val.get('members', {}).items():
                member_scheme = j.data.capnp.getMemoryObj(
                    repo_model._capnp_schema.Member, userKey=str(memberid), access=member)
                repo_model.dbobj.members.append(member_scheme)

            repo_model.dbobj.milestones = []
            for milestoneid, milestone in val.get('milestones', {}).items():
                milestone_scheme = j.data.capnp.getMemoryObj(repo_model._capnp_schema.Milestone, **milestone)
                milestone_scheme.id = milestoneid
                repo_model.dbobj.milestones.append(milestone_scheme)

            repo_model.dbobj.id = id
            repo_model.dbobj.name = val['name']
            repo_model.dbobj.description = val['description']
            repo_model.dbobj.owner = str(val['owner'])
            repo_model.dbobj.nrIssues = val['num_issues']
            repo_model.dbobj.nrMilestones = val['num_milestones']
            repo_model.dbobj.source = ''
            repo_model.save()
        else:
            del repos

    def getUsersFromPSQL(self, gogsName):
        """
        Load users from remote database into model.
        """
        self.logger.info("getUsersFromPSQL")

        if self.model == None:
            raise j.exceptions.Input(message="please connect to psql first, use self.connectPSQL",
                                     level=1, source="", tags="", msgpub="")

        for user in self.model.User.select():
            user_model = self.userCollection.getFromGogsId(gogsName=gogsName, gogsId=user.id)
            user_model.dbobj.name = user.name
            user_model.dbobj.fullname = user.full_name
            user_model.dbobj.email = user.email
            user_model.gogsRefSet(name=gogsName, id=user.id)
            user_model.dbobj.iyoId = user.name
            user_model.save()

        self.setUsersYaml(gogsName=gogsName)

    def setUsersYaml(self, gogsName):
        return
        # TODO
        res = {}
        for item in self.userCollection.find():
            res[item.key] = item.dbobj.to_dict()
            res[item.key].pop('gogsRefs')
            from IPython import embed
            print("DEBUG NOW setUsersYaml")
            embed()
            raise RuntimeError("stop debug here")

    def _getLabels(self):
        for id, name in [(item.id, item.name) for item in self.model.Label.select()]:
            self._labels[id] = name

    def getLabelFromID(self, id):
        if self._labels == {}:
            self._getLabels()
        return self._labels[id]

    def _gogsRefSet(self, model, name, id):
        """
        @param name is name of gogs instance
        @id is id in gogs
        """
        ref = self._gogsRefGet(model, name)
        if ref == None:
            model.addSubItem("gogsRefs", data=model.collection.list_gogsRefs_constructor(id=id, name=name))
        else:
            if str(ref.id) != str(id):
                raise j.exceptions.Input(
                    message="gogs id has been changed over time, this should not be possible", level=1, source="", tags="", msgpub="")

    def _gogsRefExist(self, model, name):
        return not self._gogsRefGet(model, name) == None

    def _gogsRefGet(self, model, name):
        for item in model.dbobj.gogsRefs:
            if item.name == name:
                return item
        return None

    def _getFromGogsId(self, model, gogsName, gogsId, createNew=True):
        """
        @param gogsName is the name of the gogs instance
        """
        key = model._index.lookupGet("gogs_%s" % gogsName, gogsId)
        if key == None:
            if createNew:
                user_model = model.new()
            else:
                raise j.exceptions.Input(message="cannot find object  %s from gogsid:%s" %
                                         (model.objType, gogsId), level=1, source="", tags="", msgpub="")
        else:
            user_model = model.get(key.decode())
        return user_model
