from GogsClient import GogsClient
from JumpScale import j


class GogsFactory:

    def __init__(self):
        self.__jslocation__ = "j.clients.gogs"
        self.logger = j.logger.get("j.clients.gogs")
        # self.db = ModelsFactory()
        self.model=None
        self.userCollection = j.tools.issuemanager.getUserCollectionFromDB()
        self.orgCollection = j.tools.issuemanager.getOrgCollectionFromDB()
        self.issueCollection = j.tools.issuemanager.getIssueCollectionFromDB()
        self.repoCollection = j.tools.issuemanager.getRepoCollectionFromDB()

    def getRestClient(self, addr='https://127.0.0.1', port=3000, login='root', passwd='root', accesstoken=None):
        return GogsClient(addr=addr, port=port, login=login, passwd=passwd, accesstoken=accesstoken)

    def syncAllFromPSQL(self):
        if self.model==None:
            raise j.exceptions.Input(message="please connect to psql first, use self.connectPSQL", level=1, source="", tags="", msgpub="")
        self.getIssuesFromPSQL()
        self.getUsersFromPSQL()
        self.getReposFromPSQL()
        self.getOrgsFromPSQL()

    def connectPSQL(self,ipaddr="127.0.0.1", port=5432, login="gogs", passwd="something", dbname="gogs"):
        """
        connects to psql & connects resulting model to self.model
        """
        self.model = j.clients.peewee.getModel(ipaddr=ipaddr, port=port, login=login, passwd=passwd, dbname=dbname)
        return self.model

    def getIssuesFromPSQL(self):
        """
        Load issues from remote database into model.

        @param ipaddr str,,ip address where remote database is on.
        @param port int,, port number remote database is listening on.
        @param login str,,database login.
        @param passwd str,,database passwd.
        @param dbname str,, database name.
        """

        if self.model==None:
            raise j.exceptions.Input(message="please connect to psql first, use self.connectPSQL", level=1, source="", tags="", msgpub="")

        collection = j.tools.issuemanager.getRepoCollectionFromDB()
        res=collection.list()
        if res==[]:
            #need to download
            self.getReposFromPSQL()

        model=self.model

        IssueCollection = j.tools.issuemanager.getIssueCollectionFromDB()

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
        try:
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
                                                                'content': issue.comment_content
                                                                }
        except model.User.DoesNotExist:
            from IPython import embed
            print("DEBUG NOW does not exist exception")
            embed()
            raise RuntimeError("stop debug here")

        for key, val in issues.items():
            issue_model = IssueCollection.new()
            if val['assignees']:
                issue_model.dbobj.init('assignees', len(val['assignees']))
                for count, user in enumerate(val['assignees']):
                    issue_model.dbobj.assignees[count] = user

            if val['comments']:
                issue_model.dbobj.init('comments', len(val['comments']))
                for count, (commentid, comment) in enumerate(val['comments'].items()):
                    member_scheme = issue_model.dbobj.comments[count]
                    member_scheme.owner = comment['owner']
                    member_scheme.content = comment['content']
                    member_scheme.id = commentid

            if val['labels']:
                issue_model.dbobj.init('labels', len(val['labels']))
                for count, label in enumerate(val['labels']):
                    issue_model.dbobj.labels[count] = label

            issue_model.dbobj.id = key
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

    def getOrgsFromPSQL(self):
        """
        Load organizations from remote database into model.

        @param ipaddr str,,ip address where remote database is on.
        @param port int,, port number remote database is listening on.
        @param login str,,database login.
        @param passwd str,,database passwd.
        @param dbname str,, database name.
        """

        if self.model==None:
            raise j.exceptions.Input(message="please connect to psql first, use self.connectPSQL", level=1, source="", tags="", msgpub="")

        collection = j.tools.issuemanager.getUserCollectionFromDB()
        res=collection.list()
        if res==[]:
            #need to download
            self.getUsersFromPSQL()

        OrgCollection = j.tools.issuemanager.getOrgCollectionFromDB()
        model = self.model
        queryString = """
        select org.name,
           org.full_name,
           org.id,
           org.num_repos,
           r.name as repo_name,
           r.id as repo_id,
           ou.is_owner,
           member.id as memberid,
           access.mode
        from "user" as org
        left join repository as r on org.id=r.owner_id
        left join org_user as ou on org.id=ou.org_id
        left join "user" as member on ou.uid=member.id
        left join access on member.id=access.user_id
        where org.type=1;
        """
        query = model.User.raw(queryString)
        orgs = {}
        try:
            for org in query:
                if org.name not in orgs:
                    orgs[org.id] = {'name': org.name,
                                    'description': org.full_name,
                                    'num_repos': org.num_repos,
                                    'num_members': org.num_members,
                                    'members': dict(),
                                    'repos': list(),
                                    'owners': list()
                                    }
                org_dict = orgs[org.id]
                if org.memberid:
                    org_dict['members'][org.memberid] = org.mode
                if org.is_owner and org.memberid not in org_dict['owners']:
                    org_dict['owners'].append(org.memberid)
                if org.repo_id and org.repo_id not in org_dict['repos']:
                    org_dict['repos'].append(org.repo_id)
        except model.User.DoesNotExist:
            pass

        for key, val in orgs.items():

            org_model = OrgCollection.new()
            if val['repos']:
                for count, repoid in enumerate(val['repos']):
                    from IPython import embed
                    print ("DEBUG NOW add org")
                    embed()
                    raise RuntimeError("stop debug here")
                    org_model.dbobj.repos.append(repoid)

            if val['members']:
                for count, (memberid, member) in enumerate(val['members'].items()):
                    member_scheme = org_model.dbobj.members[count]
                    member_scheme.userKey = memberid
                    member_scheme.access = member

            if val['owners']:
                org_model.dbobj.init('owners', len(val['owners']))
                for count, memberid in enumerate(val['owners']):
                    org_model.dbobj.owners[count] = memberid

            org_model.dbobj.id = key
            org_model.dbobj.name = val['name']
            org_model.dbobj.description = val['description']
            org_model.dbobj.source = ''
            org_model.save()
        else:
            del orgs

    def getReposFromPSQL(self):
        """
        Load repos from remote database into model.

        @param ipaddr str,,ip address where remote database is on.
        @param port int,, port number remote database is listening on.
        @param login str,,database login.
        @param passwd str,,database passwd.
        @param dbname str,, database name.
        """
        if self.model==None:
            raise j.exceptions.Input(message="please connect to psql first, use self.connectPSQL", level=1, source="", tags="", msgpub="")

        if self.orgCollection.list()==[]:
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
        # repos = {}
        # try:
        for repo in query:

            res=repoCollection.find(repoid=repo.id)
            from IPython import embed
            print ("DEBUG NOW i876786")
            embed()
            raise RuntimeError("stop debug here")

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
                                                              'is_closed': repo.milestone_is_closed,
                                                              'num_issues': repo.milestone_num_issues,
                                                              'num_closed_issues': repo.milestone_num_closed_issues,
                                                              'completeness': repo.milestone_completeness,
                                                              'deadline': repo.milestone_deadline}
    # except model.User.DoesNotExist:
        #     pass

        for key, val in repos.items():
            repo_model = repoCollection.new()
            if val['labels']:
                repo_model.dbobj.init('labels', len(val['labels']))
                for count, repo in enumerate(val['labels']):
                    repo_model.dbobj.labels[count] = str(repo)

            if val['members']:
                repo_model.dbobj.init('members', len(val['members']))
                for count, (memberid, member) in enumerate(val['members'].items()):
                    member_scheme = repo_model.dbobj.members[count]
                    member_scheme.userKey = str(memberid)
                    member_scheme.access = member

            if val['milestones']:
                repo_model.dbobj.init('milestones', val['num_milestones'])
                for count, (milestoneid, milestone) in enumerate(val['milestones'].items()):
                    milestone_scheme = repo_model.dbobj.milestones[count]
                    milestone_scheme.name = milestone['name']
                    milestone_scheme.isClosed = milestone['is_closed']
                    milestone_scheme.nrIssues = milestone['num_issues']
                    milestone_scheme.nrClosedIssues = milestone['num_closed_issues']
                    milestone_scheme.completeness = milestone['completeness']
                    milestone_scheme.deadline = milestone['deadline']
                    milestone_scheme.id = milestoneid

            repo_model.dbobj.id = key
            repo_model.dbobj.name = val['name']
            repo_model.dbobj.description = val['description']
            repo_model.dbobj.owner = str(val['owner'])
            repo_model.dbobj.nrIssues = val['num_issues']
            repo_model.dbobj.nrMilestones = val['num_milestones']
            repo_model.dbobj.source = ''
            repo_model.save()
        else:
            del repos

    def getUsersFromPSQL(self):
        """
        Load users from remote database into model.
        """
        if self.model==None:
            raise j.exceptions.Input(message="please connect to psql first, use self.connectPSQL", level=1, source="", tags="", msgpub="")

        for user in self.model.User.select():

            user_model=self.userCollection.getFromId(user.id,defaultNewMethod=self.userCollection.new)

            user_model.dbobj.name = user.name
            user_model.dbobj.fullname = user.full_name
            user_model.dbobj.email = user.email
            user_model.dbobj.id = user.id
            user_model.dbobj.source = ''
            user_model.save()
