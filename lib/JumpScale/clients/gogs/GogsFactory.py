from GogsClient import GogsClient
from JumpScale import j
import psycopg2


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
        self._issue_user_table = {}
        self._users_table = {}
        self._milestones_table = {}
        self._repos_table = {}

        self.dbconn = None

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


        -- create aggregated view for orgs
        CREATE OR REPLACE VIEW org_users_grouped AS
        SELECT
          org_id,
          array_to_string(array_agg(uid), ',')
        FROM
          public.org_user
        GROUP BY org_id
        ORDER BY org_id;

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
        self.logger.info("CreateViews")
        self.createViews()
        self.logger.info("Users Table")
        self.users_table
        self.logger.info("Issue User Table")
        self.issue_user_table
        self.logger.info("Milestones")
        self.milestones_table
        self.logger.info("Users")
        self.getUsersFromPSQL(gogsName=gogsName)
        self.logger.info("User synced")
        self.getOrgsFromPSQL(gogsName=gogsName)
        self.logger.info("Organizations synced")
        self.getReposFromPSQL(gogsName=gogsName)
        self.logger.info("Repositories synced")
        self.getIssuesFromPSQL(gogsName=gogsName)
        self.logger.info("Issues synced")

    @property
    def users_table(self):
        """
        is dict, key is $userid data is ()
        """
        if self._users_table == {}:
            for user in self.model.User:
                self._users_table[user.id] = user
        return self._users_table

    @property
    def issue_user_table(self):
        """
        is dict, key is $issueid_userid data is (repoid,milestoneid,is_read,is_assigned,is_mentioned,is_poster,is_closed)
        """
        if self._issue_user_table == {}:
            for item in self.model.IssueUser:
                self._issue_user_table[item.id] = item
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
        self.logger.info("getOrgsFromPSQL")

        cur = self.dbconn.cursor()
        cur.execute("select * from org_users_grouped;")
        rows = cur.fetchall()

        for orgIdAsUser, userIds in rows:
            orgName = self.users_table[orgIdAsUser].name
            self.logger.debug(row.__dict__)

            # get organization from gogsid
            org_model = self.orgCollection.getFromGogsId(gogsName=gogsName, gogsId=orgIdAsUser)
            # org_model.gogsRefSet(name=gogsName, id=orgIdAsUser)

            # # get member (user) from gogs id
            # member_model = self.userCollection.getFromGogsId(
            #     gogsName=gogsName, gogsId=org.member_id, createNew=False)  # member needs to exists

            # # set member on the org model
            # org_model.memberSet(member_model.key, org.member_access)

            if org_model.dbobj.name != orgName:
                org_model.dbobj.name = orgName
                org_model.changed = True

            org_model.gogsRefSet(name=gogsName, id=org.id)

            # # process the repoobj
            # repo_model = self.repoCollection.getFromGogsId(gogsName=gogsName, gogsId=org.repo_id)
            # if repo_model.dbobj.name != org.repo_name:
            #     repo_model.dbobj.name = org.repo_name
            #     repo_model.changed = True
            #
            # repo_model.gogsRefSet(name=gogsName, id=int(org.repo_id))  # mark info comes from gogs
            # repo_model.save()

            # if org_model.dbobj.nrRepos != org.num_repos:
            #     org_model.dbobj.nrRepos = org.num_repos
            #
            # if org.is_owner:
            #     org_model.ownerSet(member_model.key)
            #
            # org_model.repoSet(repo_model.key)

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

        for id, repo in self.repos_table.items():
            repo_model = self.repoCollection.getFromId(id)

            repo_model.dbobj.id = id
            repo_model.dbobj.name = repo_model.name
            repo_model.dbobj.description = repo_model.description
            repo_model.dbobj.owner = repo_model.owner
            repo_model.dbobj.nrIssues = repo_model.num_issues
            repo_model.dbobj.nrMilestones = repo_model.num_milestones
            # source TODO
            repo_model.save()

        from IPython import embed
        print("DEBUG NOW getReposFromPSQL")
        embed()
        raise RuntimeError("stop debug here")

    def getUsersFromPSQL(self, gogsName):
        """
        Load users from remote database into model.
        """
        self.logger.info("getUsersFromPSQL")

        if self.model == None:
            raise j.exceptions.Input(message="please connect to psql first, use self.connectPSQL",
                                     level=1, source="", tags="", msgpub="")

        for id, user in self.users_table.items():
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

    # def _getLabels(self):
    #     for id, name in [(item.id, item.name) for item in self.model.Label.select()]:
    #         self._labels[id] = name
    #
    # def getLabelFromID(self, id):
    #     if self._labels == {}:
    #         self._getLabels()
    #     return self._labels[id]

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
