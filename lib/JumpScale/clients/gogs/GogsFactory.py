from GogsClient import GogsClient
from JumpScale import j
import psycopg2
import sys


class GogsFactory:

    def __init__(self):
        self.__jslocation__ = "j.clients.gogs"
        self.logger = j.logger.get("j.clients.gogs")
        self.model = None

        self.logger = j.logger.get("j.clients.gogs")
        self.logger.info("gogs factory initted.")
        self.dbconn = None
        self.reset()

    def reset(self):
        self._labels = {}
        self._issue_user_table = {}
        self._users_table = {}
        self._milestones_table = {}
        self._repos_table = {}
        self.userId2userKey = {}
        self.repoId2repoKey = {}
        self.userCollection = j.tools.issuemanager.getUserCollectionFromDB()
        self.orgCollection = j.tools.issuemanager.getOrgCollectionFromDB()
        self.issueCollection = j.tools.issuemanager.getIssueCollectionFromDB()
        self.repoCollection = j.tools.issuemanager.getRepoCollectionFromDB()

    def createViews(self):
        self.logger.info("createviews")

        self.model.User.raw("DROP VIEW IF EXISTS issue_labels CASCADE; ").execute()
        self.model.User.raw("DROP VIEW IF EXISTS issue_labels_grouped CASCADE ;").execute()
        self.model.User.raw("DROP VIEW IF EXISTS issue_comments CASCADE ;").execute()
        self.model.User.raw("DROP VIEW IF EXISTS issue_comments_grouped CASCADE ;").execute()
        self.model.User.raw("DROP VIEW IF EXISTS org_users_grouped CASCADE ;").execute()
        self.model.User.raw("DROP VIEW IF EXISTS issues_view CASCADE ;").execute()

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
          array_to_string(array_agg(label_name), ',') as labels
        FROM
          public.issue_labels
        GROUP BY id
        ORDER BY id;

        -- view of comments
        CREATE OR REPLACE VIEW issue_comments AS
        SELECT
          issue.id,
          '{' || comment.id || ',' || comment.poster_id || ',' || comment.created_unix || ',' || comment.updated_unix || '}' || comment.content as comment
        FROM issue
        left join comment on issue.id=comment.issue_id
        ORDER by comment.id;

        -- create aggregated view for comments (returns {$commentid,$committerid}||,...)
        CREATE OR REPLACE VIEW issue_comments_grouped AS
        SELECT
          id,
          array_to_string(array_agg(comment), '||') as comments
        FROM
          public.issue_comments
        GROUP BY id
        ORDER BY id;


        -- create aggregated view for orgs
        CREATE OR REPLACE VIEW org_users_grouped AS
        SELECT
          org_id as org_userid,
          array_to_string(array_agg(uid), ',') as org_member_userids
        FROM
          public.org_user
        GROUP BY org_userid
        ORDER BY org_userid;

        -- create aggregated view for issues
        CREATE OR REPLACE VIEW issues_view AS
        SELECT
          issue_labels_grouped.labels,
          encode(convert_to(issue_comments_grouped.comments,'UTF8'),'base64') AS comments,
          issue.id,
          issue.repo_id,
          issue.poster_id,
          encode(convert_to(issue.name,'UTF8'),'base64') AS name,
          encode(convert_to(issue.content,'UTF8'),'base64') AS content,
          issue.milestone_id,
          issue.priority,
          issue.assignee_id,
          issue.is_closed,
          issue.is_pull,
          issue.num_comments,
          issue.deadline_unix,
          issue.created_unix,
          issue.updated_unix,
          issue.index
        FROM
          public.issue,
          public.issue_comments_grouped,
          public.issue_labels_grouped
        WHERE
          issue.id = issue_comments_grouped.id AND
          issue.id = issue_labels_grouped.id;


        """

        query = self.model.User.raw(C)
        query.execute()

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

    def syncAllFromPSQL(self, git_host_name):
        if self.model == None:
            raise j.exceptions.Input(message="please connect to psql first, use self.connectPSQL",
                                     level=1, source="", tags="", msgpub="")
        self.logger.info("syncAllFromPSQL")
        self.logger.info("CreateViews")
        self.createViews()

        # will also create user_table & self.userId2userKey
        self.getUsersFromPSQL(git_host_name=git_host_name)
        self.logger.info("Users Synced")

        self.milestones_table
        self.logger.info("Milestones Done")

        self.getOrgsFromPSQL(git_host_name=git_host_name)
        self.logger.info("Organizations synced")

        self.getReposFromPSQL(git_host_name=git_host_name)
        self.logger.info("Repositories synced")

        self.getIssuesFromPSQL(git_host_name=git_host_name)
        self.logger.info("Issues synced")

        self.reset()

    @property
    def users_table(self):
        """
        is dict, key is $userid data is ()
        """
        if self._users_table == {}:
            try:
                for user in self.model.User:
                    print("user:%s" % user.name)
                    self._users_table[user.id] = user
            except Exception as e:
                print("WARNING: could download user:%s" % user.name, sep=' ', end='n', file=sys.stdout, flush=False)
        return self._users_table

    @property
    def issue_user_table(self):
        """
        is dict, key is $issueid_userid data is (repoid,milestoneid,is_read,is_assigned,is_mentioned,is_poster,is_closed)
        """
        if self._issue_user_table == {}:
            try:
                for item in self.model.Issue:
                    self.logger.info("process issue_userp:%s" % item.name)
                    self._issue_user_table.setdefault(item.id, [])
                    self._issue_user_table[item.id].append(item)
            except Exception as e:
                self.logger.error("ERROR: could download issue_user:%s" % item.name)
                sys.exit(1)

        return self._issue_user_table

    @property
    def repos_table(self):
        """
        is dict, key is $issueid_userid data is (repoid,milestoneid,is_read,is_assigned,is_mentioned,is_poster,is_closed)
        """
        if self._repos_table == {}:
            for item in self.model.Repository:
                self._repos_table[item.id] = item
        return self._repos_table

    @property
    def milestones_table(self):
        """
        is dict, key is $issueid_userid data is (repoid,milestoneid,is_read,is_assigned,is_mentioned,is_poster,is_closed)
        """
        if self._milestones_table == {}:
            for item in self.model.Milestone:
                self._milestones_table[item.id] = item
        return self._milestones_table

    def connectPSQL(self, ipaddr="127.0.0.1", port=5432, login="gogs", passwd="something", dbname="gogs"):
        """
        connects to psql & connects resulting model to self.model
        is a peewee orm enabled orm
        """
        self.model = j.clients.peewee.getModel(ipaddr=ipaddr, port=port, login=login, passwd=passwd, dbname=dbname)
        self.dbconn = psycopg2.connect(
            "dbname='%s' user='%s' host='localhost' password='%s' port='%s'" % (dbname, login, passwd, port))
        return self.model

    def getIssuesFromPSQL(self, git_host_name):
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

        query = self.model.Issue.raw("SET CLIENT_ENCODING TO 'UTF8';select * from issues_view order by id;")

        for issue in query:

            repo = self.repos_table[issue.repo_id]
            repoName = repo.name

            orgName = self.users_table[repo.owner].name

            name = j.data.serializer.base64.loads(issue.name)

            self.logger.debug("process issue: org:%s %s/%s %s" % (orgName, repoName, issue.id, name))

            issueIdLocal = issue.index
            url = "https://docs.greenitglobe.com/%s/%s/issues/%s" % (orgName, repoName, issueIdLocal)
            issue_model = self.issueCollection.getFromGitHostID(git_host_name, issue.id, url, createNew=True)

            issue.repo = issue.repo_id
            # assignees
            if issue.id in self.issue_user_table:
                assignees = [self.userId2userKey.get(item.assignee, "") for item in self.issue_user_table[issue.id]]
                for assignee in assignees:
                    issue_model.assigneeSet(assignee)

            if issue_model.dbobj.isClosed != issue.is_closed:
                issue_model.dbobj.isClosed = issue.is_closed
                issue_model.changed = True

            mod_time = int(issue.updated_unix)

            # our view has pre-aggregrated the comments, need to do some minimal parsing now
            comments = j.data.serializer.base64.loads(issue.comments)
            comments = [item.strip() for item in comments.split("||") if item.strip() != ""]
            comments.sort()  # will make sure its sorted on comment_id (prob required for right order of comments)

            for comment in comments:
                res = comment.split("}")
                if len(res) == 2:
                    meta, comment = res
                    _, owner_id, created, modified = meta.split(',')
                    owner = self.userId2userKey.get(owner_id, '')
                    modified = int(modified)
                    if modified > mod_time:
                        mod_time = modified
                    # owner = self.users_table[ownerId].id
                else:
                    comment = res[0]
                    owner = ""
                    modified = None
                issue_model.commentSet(comment, owner=owner, modTime=modified)

            if issue.milestone_id != 0:
                milestone = self.milestones_table[issue.milestone_id].name
                if issue_model.dbobj.milestone != milestone:
                    self.logger.debug("milestone changed")
                    issue_model.dbobj.milestone = milestone

            if issue_model.dbobj.title != name:
                self.logger.debug("title changed")
                issue_model.dbobj.title = name
                issue_model.changed = True

            if issue.labels != '':
                labels = [item.strip() for item in issue.labels.split(",") if item.strip() != ""]
                labels.sort()
                issue_model.initSubItem("labels")
                if not ",".join(issue_model.list_labels) == ",".join(labels):
                    self.logger.debug("labels changed")
                    issue_model.list_labels = []
                    for label in labels:
                        issue_model.list_labels.append(label)
                    issue_model.changed = True

            issue_model.dbobj.creationTime = issue.created_unix

            if issue_model.dbobj.modTime != mod_time:
                issue_model.dbobj.modTime = mod_time
                issue_model.changed = True

            content = j.data.serializer.base64.loads(issue.content)
            if issue_model.dbobj.content != content:
                issue_model.dbobj.content = content
                issue_model.changed = True

            if issue_model.dbobj.isClosed != issue.is_closed:
                issue_model.dbobj.isClosed = issue.is_closed
                issue_model.changed = True

            issue_model.dbobj.repo = repo.name

            issue_model.save()

    def getOrgsFromPSQL(self, git_host_name):
        self.logger.info("getOrgsFromPSQL")

        query = self.model.OrgUser.raw("select * from org_users_grouped;")

        if self.userId2userKey == {}:
            self.getUsersFromPSQL(git_host_name=git_host_name)

        for org in query:

            orgName = self.users_table[org.org_userid].name

            # get organization from git_host_id
            url = "https://docs.greenitglobe.com/%s" % orgName
            org_model = self.orgCollection.getFromGitHostID(
                git_host_name=git_host_name, git_host_id=org.org_userid, git_host_url=url)

            members = [self.userId2userKey[int(item.strip())]
                       for item in org.org_member_userids.split(",")]
            members = members.sort()

            if org_model.dbobj.members != members:
                self.logger.debug("org members changed :%s" % orgName)
                org_model.initSubItem("members")
                org_model.list_members = members
                org_model.changed = True

            if org_model.dbobj.name != orgName:
                self.logger.debug("org name changed:%s" % orgName)
                org_model.dbobj.name = orgName
                org_model.changed = True

            org_model.save()

    def getReposFromPSQL(self, git_host_name):
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

        if self.userId2userKey == {}:
            self.getUsersFromPSQL(git_host_name=git_host_name)

        for id, repo in self.repos_table.items():

            url = "https://docs.greenitglobe.com/%s/%s" % (self.userId2userKey[repo.owner], repo.name)
            repo_model = self.repoCollection.getFromGitHostID(
                git_host_name=git_host_name, git_host_id=id, git_host_url=url)

            repo_model.dbobj.name = repo.name
            repo_model.dbobj.description = repo.description
            repo_model.dbobj.owner = self.userId2userKey[repo.owner]
            repo_model.dbobj.nrIssues = repo.num_issues
            repo_model.dbobj.nrMilestones = repo.num_milestones
            repo_model.changed = True

            self.repoId2repoKey[id] = repo_model.key

            repo_model.save()

    def getUsersFromPSQL(self, git_host_name):
        """
        Load users from remote database into model.
        """
        self.logger.info("getUsersFromPSQL")

        if self.model == None:
            raise j.exceptions.Input(message="please connect to psql first, use self.connectPSQL",
                                     level=1, source="", tags="", msgpub="")

        for id, user in self.users_table.items():
            url = "https://docs.greenitglobe.com/%s" % user.name
            user_model = self.userCollection.getFromGitHostID(
                git_host_name=git_host_name, git_host_id=user.id, git_host_url=url)
            if user_model.dbobj.name != user.name:
                user_model.dbobj.name = user.name
                user_model.changed = True
            if user_model.dbobj.fullname != user.full_name:
                user_model.dbobj.fullname = user.full_name
                user_model.changed = True
            if user_model.dbobj.email != user.email:
                user_model.dbobj.email = user.email
                user_model.changed = True
            # user_model.gitHostRefSet(name=git_host_name, id=user.id)
            if user_model.dbobj.iyoId != user.name:
                user_model.dbobj.iyoId = user.name
                user_model.changed = True

            user_model.save()

            self.userId2userKey[id] = user_model.key

        self.setUsersYaml(git_host_name=git_host_name)

    def setUsersYaml(self, git_host_name):
        return
        # TODO is to allow to put additional info to users
        res = {}
        for item in self.userCollection.find():
            res[item.key] = item.dbobj.to_dict()
            res[item.key].pop('gitHostRefs')
            from IPython import embed
            print("DEBUG NOW setUsersYaml")
            embed()
            raise RuntimeError("stop debug here")

    def _gitHostRefSet(self, model, git_host_name, git_host_id, git_host_url):
        """
        @param name is name of gogs instance
        @id is id in gogs
        """
        model.logger.debug("gitHostRefSet: git_host_name='%s' git_host_id='%s' git_host_url='%s'" %
                           (git_host_name, git_host_id, git_host_url))
        ref = self._gitHostRefGet(model, git_host_name, git_host_url)
        if ref == None:
            model.addSubItem("gitHostRefs", data=model.collection.list_gitHostRefs_constructor(
                id=git_host_id, name=git_host_name, url=git_host_url))
            key = model.collection._index.lookupSet("githost_%s" % git_host_name, git_host_id, model.key)
            model.save()
        else:
            if str(ref.id) != str(id):
                raise j.exceptions.Input(
                    message="gogs id has been changed over time, this should not be possible", level=1, source="", tags="", msgpub="")

    def _gitHostRefExists(self, model, git_host_name):
        return not self._gitHostRefGet(model, git_host_name) == None

    def _gitHostRefGet(self, model, git_host_name, git_host_url):
        for item in model.dbobj.gitHostRefs:
            if item.name == git_host_name:
                return item
        return None

    def _getFromGitHostID(self, modelCollection, git_host_name, git_host_id, git_host_url, createNew=True):
        """
        @param git_host_name is the name of the gogs instance
        """
        modelCollection.logger.debug("gitHostRefSet: git_host_name='%s' git_host_id='%s' git_host_url='%s'" % (
            git_host_name, git_host_id, git_host_url))
        key = modelCollection._index.lookupGet("githost_%s" % git_host_name, git_host_id)
        if key == None:
            modelCollection.logger.debug("githost id not found, create new")
            if createNew:
                modelActive = modelCollection.new()
                self._gitHostRefSet(model=modelActive, git_host_name=git_host_name,
                                    git_host_id=git_host_id, git_host_url=git_host_url)
            else:
                raise j.exceptions.Input(message="cannot find object  %s from git_host_id:%s" %
                                         (modelCollection.objType, git_host_id), level=1, source="", tags="", msgpub="")
        else:
            modelActive = modelCollection.get(key.decode())
        return modelActive
