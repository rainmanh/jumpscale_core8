from JumpScale import j
from JumpScale.tools.zip.ZipFile import ZipFile
from multiprocessing.pool import ThreadPool as Pool
from Repository import GithubRepo
from User import User
from Issue import Issue
from datetime import datetime

def githubtimetoint(t):
    #parsed = datetime.strptime(t, "%Y-%m-%d %I:%M:%S")
    return j.data.time.any2epoch(t)

try:
    import github
except:
    cmd = "pip3 install pygithub"
    j.sal.process.execute(cmd)
    import github


def fetchall_from_paginated_list(paginated_list):
    """
    Eagrly fetch all the items from paginated list (Github API paged responses)

    @param paginated_list PaginatedList: paginated list object.
    """
    els = []
    idx = 0
    while True:
        vals = paginated_list.get_page(idx)
        if not vals:
            break
        else:
            els.extend(vals)
            idx += 1
    return els


def fetchall_from_many_paginated_lists(*paginated_lists):
    """
    Fetch all items from many paginated lists and flatten them out.

    @param paginated_lists list: list of paginated lists objects.
    """
    els = []
    for p in paginated_lists:
        els.extend(fetchall_from_paginated_list(p))
    return els

class GitHubFactory:

    def __init__(self):
        self.__jslocation__ = "j.clients.github"
        self._clients = {}

    # def getRepoClient(self, account, reponame):
    #     return GitHubRepoClient(account, reponame)

    def getClient(self, secret):
        if secret not in self._clients:
            self._clients[secret] = GitHubClient(secret)
        return self._clients[secret]

    def getIssueClass(self):
        return Issue


class GitHubClient:

    def __init__(self, secret):
        self.api = github.Github(secret, per_page=100)
        self.users = {}
        self.repos = {}
        self.pool = Pool()

        self.model = None
        j.tools.issuemanager.set_namespaceandstore("github", "github")

        self.userCollection = j.tools.issuemanager.getUserCollectionFromDB()

        self.orgCollection = j.tools.issuemanager.getOrgCollectionFromDB()
        self.issueCollection = j.tools.issuemanager.getIssueCollectionFromDB()
        self.repoCollection = j.tools.issuemanager.getRepoCollectionFromDB()

    def getRepo(self, fullname):
        """
        fullname e.g. incubaid/myrepo
        """
        if fullname not in self.repos:
            r = GithubRepo(self, fullname)
            self.repos[fullname] = r
        return self.repos[fullname]

    def getUserLogin(self, githubObj):
        if githubObj is None:
            return ""
        if githubObj.login not in self.users:
            user = User(self, githubObj=githubObj)
            self.users[githubObj.login] = user
        return self.users[githubObj.login].login

    def getUser(self, login="", githubObj=None):
        if login in self.users:
            return self.users[login]

        if githubObj is not None:
            if githubObj.login not in self.users:
                user = User(self, githubObj=githubObj)
                self.users[githubObj.login] = user
            return self.users[githubObj.login]


    def _getUsersFromGithubOrg(self, org):
        """
        populates user models from github organization.

        @param org str: organization name.

        """
        org = self.api.get_organization(org)
        members_pagedlist = org.get_members()

        members = fetchall_from_paginated_list(members_pagedlist)

        for user in members:
            user_model = self.userCollection.getFromId(user.id)
            user_model.dbobj.name = user.login
            user_model.dbobj.fullname = user.name or ''
            user_model.dbobj.email = user.email or ''
            user_model.dbobj.id = user.id
            user_model.dbobj.source = ''
            user_model.save()

    # FIX ALL NR_FIELDS TO USE totalCount attr
    def _getOrganizationFromGithub(self, orgname):
        """
        populate organization model from Github organization name.

        @param orgname str: organization name.
        """
        org = self.api.get_organization(orgname)
        allissues = fetchall_from_paginated_list(org.get_issues())
        nrissues = len(allissues)

        orgid = org.id
        #  nr of milestones => set of all milestones in all repos?
        repos = fetchall_from_paginated_list(org.get_repos())
        reposids = [repo.id for repo in repos]

        milestones = set([m.title for m in fetchall_from_many_paginated_lists(*[rep.get_milestones() for rep in repos])])
        nrmilestones = len(milestones)
        description = orgname # FIXME: how to get a description of an org? orgname used instead.
        members = fetchall_from_paginated_list(org.get_members())
        nrmembers = len(members)

        # FIXME: calculate owners ids list.
        owners = []

        org_model = self.orgCollection.getFromId(orgid)
        org_model.dbobj.repos = reposids

        org_model.dbobj.members = []
        for member in members:
            member_scheme = j.data.capnp.getMemoryObj(org_model._capnp_schema.Member, userKey=member.id, access=0)
            org_model.members.append(member_scheme)

        org_model.dbobj.owners = owners
        org_model.dbobj.id = orgid
        org_model.dbobj.name = orgname
        org_model.dbobj.description = description
        org_model.dbobj.source = ''
        org_model.save()

    def getUsersFromGithubOrgs(self, *orgs):
        """
        Populates user models from a list of github organizations.

        @param orgs list: list of organizations names.

        """
        # list(map(self._getUsersFromGithubOrg, orgs))
        self.pool.map(self._getUsersFromGithubOrg, orgs)

    def getOrgsFromGithub(self, *orgs):
        """
        Populates organization models from github organizations names list.

        @param orgs list: list of organizations names.
        """
        self.pool.map(self._getOrganizationFromGithub, orgs)


    def getIssuesFromGithubRepo(self, repo):
        """
        Populates issues models from github repo.

        @param repo str: github repository name.

        """
        repo = self.getRepo(repo)
        repoid = repo.api.id

        def process_issue_from_github(issue):
            """
            Process issue from github issue.

            @param issue Issue: issue object.
            """

            issue_model = self.issueCollection.getFromId(issue.id)
            issue_model.dbobj.assignees = [user.id for user in issue.api.assignees]

            for comment in issue.comments:
                # FIX COMMNET OBJECT CREATION
                comment_scheme = j.data.capnp.getMemoryObj(issue_model._capnp_schema.Comment, content=comment['body'], id=comment['id'], owner=comment['user_id'])
                issue_model.dbobj.comments.append(comment_scheme)

            issue_model.dbobj.labels = issue.labels
            issue_model.dbobj.id = issue.id
            issue_model.dbobj.title = issue.title
            issue_model.dbobj.content = issue.body
            milestoneid = 0
            if issue.api.milestone:
                    milestoneid = issue.api.milestone.id
            issue_model.dbobj.milestone = milestoneid
            issue_model.dbobj.isClosed = issue.state == 'closed'
            issue_model.dbobj.repo = repoid
            issue_model.dbobj.creationTime = 0 #githubtimetoint(issue.api.created_at)
            issue_model.dbobj.modTime = 0 #githubtimetoint(issue.api.updated_at)
            issue_model.dbobj.source = ''
            try:
                issue_model.save()
            except Exception as ex:
                print("Exception: ", ex)
                #import ipdb; ipdb.set_trace()
        pool = Pool(50)
        pool.map(process_issue_from_github, repo.issues)


    def getIssuesFromGithubOrganization(self, org):
        """
        Populates all issues from github organization org

        @param org str: organization name.
        """
        org = self.api.get_organization(org)
        repos = fetchall_from_paginated_list(org.get_repos())
        self.pool.map(self.getIssuesFromGithubRepo, [rep.full_name for rep in repos])

    def getIssuesFromGithubOrganizations(self, *orgs):
        """
        Populates all issues from github organizations list orgs.

        @param orgs list[str]: list of organizations names.
        """
        self.pool.map(self.getIssuesFromGithubOrganization, orgs)

    def getReposFromGithubOrgs(self, *orgs):
        """
        Populate repos models from list of organizations names.

        @param orgs list[str]: list of organizations names.

        """
        self.pool.map(self.getReposFromGithubOrg, orgs)

    def getReposFromGithubOrg(self, org):
        """
        Populates repos from organization.

        @param org str: organization names.

        """
        org = self.api.get_organization(org)
        repos = fetchall_from_paginated_list(org.get_repos())
        self.pool.map(self.getRepoFromGithubRepo, [rep.full_name for rep in repos])

    def getRepoFromGithubRepo(self, repo):
        """
        Populate repo model from github repository.

        @param repo str: repository name.
        """
        repo = self.getRepo(repo)
        owner = repo.api.owner

        repoid = repo.api.id
        labels = fetchall_from_paginated_list(repo.api.get_labels())
        milestones = fetchall_from_paginated_list(repo.api.get_milestones())


        repo_model = self.repoCollection.getFromId(repoid)
        repo_model.dbobj.labels = [lbl.name for lbl in labels]


        # HOW TO CALCULATE THE MEMBERS OF REPO? or should check the members of the team in it's parent org?
        members = []
        repoorg = repo.api.organization
        if repoorg.name is not None:
            members = fetchall_from_paginated_list(repoorg.get_members())
        repo_model.dbobj.members = []
        for member in members:
            member_scheme = j.data.capnp.getMemoryObj(repo_model._capnp_schema.Member, userKey=str(member.id), access=0)
            repo_model.dbobj.members.append(member_scheme)


        repo_model.dbobj.milestones = []
        for milestone in milestones:
            nrclosedissues = milestone.closed_issues
            nropenissues = milestone.open_issues
            nrallissues = nropenissues + nrclosedissues
            ncomplete = 100
            if nrallissues>0:
                ncomplete = int(100*nrclosedissues/nrallissues)
            md = {
                "name": milestone.title,
                "id": milestone.id,
                "deadline": githubtimetoint(milestone.due_on),
                "isClosed": milestone.state!="open",
                "nrIssues": nropenissues + nrclosedissues,
                "nrClosedIssues": nrclosedissues,
                "completeness" : ncomplete #ceil(nrClosedIssuesForThisMilestone/); #in integer (0-100)
            }
            milestone_scheme = j.data.capnp.getMemoryObj(repo_model._capnp_schema.Milestone, **md)
            milestone_scheme.id = milestone.id
            repo_model.dbobj.milestones.append(milestone_scheme)

        repo_model.dbobj.id = repoid
        repo_model.dbobj.name = repo.name
        repo_model.dbobj.description = repo.name
        repo_model.dbobj.owner = owner.login
        repo_model.dbobj.nrIssues = len(repo.issues)
        repo_model.dbobj.nrMilestones = len(milestones)
        repo_model.dbobj.source = ''
        repo_model.save()
