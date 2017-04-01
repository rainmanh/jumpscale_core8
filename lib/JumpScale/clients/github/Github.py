from JumpScale import j
from JumpScale.tools.zip.ZipFile import ZipFile
from multiprocessing.pool import ThreadPool as Pool
from Repository import GithubRepo
from User import User
from Issue import Issue
from datetime import datetime
import itertools


# please note you need to use ModelBase1 for now.
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

    def getClient(self, login_or_token, password=None):
        if login_or_token not in self._clients:
            self._clients[login_or_token] = GitHubClient(login_or_token, password)
        return self._clients[login_or_token]

    def getIssueClass(self):
        # return Issue
        return


class GitHubClient:

    def __init__(self, login_or_token, password=None):
        self.api = github.Github(login_or_token, password, per_page=100)
        self.users = {}
        self.repos = {}
        self.milestones = {}
        self.pool = Pool()

        self.model = None
        # j.tools.issuemanager.set_namespaceandstore("github", "github")

        self.userCollection = j.tools.issuemanager.getUserCollectionFromDB()
        self.orgCollection = j.tools.issuemanager.getOrgCollectionFromDB()
        self.issueCollection = j.tools.issuemanager.getIssueCollectionFromDB()
        self.repoCollection = j.tools.issuemanager.getRepoCollectionFromDB()
        self.logger = j.logger.get('j.clients.github')

    # def getRepo(self, fullname):
    #     """
    #     fullname e.g. incubaid/myrepo
    #     """
    #     if fullname not in self.repos:
    #         r = self.api.get_repo(fullname)
    #         self.repos[fullname] = r
    #     return self.repos[fullname]

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

    def getUsersFromGithubOrg(self, org):
        """
        populates user models from github organization.

        @param org str: organization name.

        """
        self.logger.info("get users from github org:%s" % org)
        git_host_name = "github"
        org = self.api.get_organization(org)
        members_pagedlist = org.get_members()

        members = fetchall_from_paginated_list(members_pagedlist)

        for user in members:
            url = "https://github.com/%s" % user.login
            user_model = self.userCollection.getFromGitHostID(
                git_host_name=git_host_name, git_host_id=user.id, git_host_url=url)
            if user_model.dbobj.name != user.login:
                user_model.dbobj.name = user.login
                user_model.changed = True
            if user.name and user_model.dbobj.fullname != user.name:
                user_model.dbobj.fullname = user.name
                user_model.changed = True
            if user.email and user_model.dbobj.email != user.email:
                user_model.dbobj.email = user.email
                user_model.changed = True
            # user_model.gitHostRefSet(name=git_host_name, id=user.id)
            # if user_model.dbobj.iyoId != user.login:
            #     user_model.dbobj.iyoId = user.login
                # user_model.changed = True
            if user_model.dbobj.inGithub != True:
                user_model.dbobj.inGithub = True
                user_model.changed = True
            user_model.save()

            self.users[user.login] = user_model.key

    # FIX ALL NR_FIELDS TO USE totalCount attr
    def _getOrganizationFromGithub(self, orgname):
        """
        populate organization model from Github organization name.

        @param orgname str: organization name.
        """
        git_host_name = "github"
        if not self.users:
            self._getUsersFromGithubOrg(git_host_name, orgname)

        org = self.api.get_organization(orgname)
        allissues = fetchall_from_paginated_list(org.get_issues())
        nrissues = len(allissues)

        orgid = org.id

        url = 'https://github.com/%s' % orgname
        org_model = self.orgCollection.getFromGitHostID(
            git_host_name=git_host_name, git_host_id=org.id, git_host_url=url)

        # org_model.dbobj.repos = reposids

        # repos = fetchall_from_paginated_list(org.get_repos())
        # if org_model.dbobj.repos != repos:
        #     org_model.initSubItem("repos")
        #     org_model.list_repos = repos
        #     org_model.changed = True

        # milestones = set([m.title for m in fetchall_from_many_paginated_lists(*[rep.get_milestones() for rep in repos])])
        #  nr of milestones => set of all milestones in all repos?
        # nrmilestones = len(milestones)

        description = orgname  # FIXME: how to get a description of an org? orgname used instead.

        members = fetchall_from_paginated_list(org.get_members())
        nrmembers = len(members)
        members = [self.users[item.login]
                   for item in members]
        members = members.sort()

        # FIXME: calculate owners ids list.
        owners = []

        if org_model.dbobj.members != members:
            org_model.initSubItem("members")
            org_model.list_members = members
            org_model.changed = True

        if org_model.dbobj.name != orgname:
            org_model.dbobj.name = orgname
            org_model.changed = True

        # org_model.dbobj.owners = owners
        # org_model.dbobj.key = orgid
        org_model.dbobj.inGithub = True
        org_model.dbobj.description = org.raw_data['description'] or ''
        org_model.save()

    def getUsersFromGithubOrgs(self, *orgs):
        """
        Populates user models from a list of github organizations.

        @param orgs list: list of organizations names.

        """
        git_host_name = "github"
        for org in orgs:
            self.getUsersFromGithubOrg(org)
        # self.pool.starmap(self.getUsersFromGithubOrg, zip(orgs))
        from IPython import embed
        print("DEBUG NOW oi")
        embed()
        raise RuntimeError("stop debug here")

    def getOrgsFromGithub(self, *orgs):
        """
        Populates organization models from github organizations names list.

        @param orgs list: list of organizations names.
        """
        git_host_name = "github"
        self.pool.starmap(self._getOrganizationFromGithub, zip(itertools.repeat(git_host_name), orgs))

    def getIssuesFromGithubRepo(self, repo):
        """
        Populates issues models from github repo.

        @param repo str: github repository name.

        """
        git_host_name = "github"
        if not self.repos:
            self.getReposFromGithubOrgs(git_host_name)

        repo = self.api.get_repo(repo)

        def process_issue_from_github(issue):
            """
            Process issue from github issue.

            @param issue Issue: issue object.
            """

            url = 'https://github.com/%s/issues/%s' % (issue.repository.full_name, issue.number)
            issue_model = self.issueCollection.getFromGitHostID(
                git_host_name=git_host_name, git_host_id=issue.id, git_host_url=url)
            issue_model.dbobj.assignees = [self.users[user.login] for user in issue.assignees]

            # our view has pre-aggregrated the comments, need to do some minimal parsing now
            comments = fetchall_from_paginated_list(issue.get_comments())
            # comments.sort(key=lambda comment:comment.id)  # will make sure its
            # sorted on comment_id (prob required for right order of comments)
            if comments != []:
                for comment in comments:
                    issue_model.commentSet(comment.body, owner=self.users.get(comment.user.login))

            issue_model.dbobj.milestone = issue.milestone.title if issue.milestone else ''

            issue_model.dbobj.labels = [label.name for label in issue.labels]
            issue_model.dbobj.title = issue.title or ''
            issue_model.dbobj.content = issue.body.replace('!', '\!') if issue.body else ''
            issue_model.dbobj.isClosed = issue.state == 'closed'
            issue_model.dbobj.repo = self.repos[issue.repository.full_name]
            issue_model.dbobj.inGithub = True
            issue_model.changed = True
            issue_model.save()

        issues = fetchall_from_paginated_list(repo.get_issues())
        pool = Pool(50)
        pool.map(process_issue_from_github, issues)

    def getIssuesFromGithubOrganization(self, org):
        """
        Populates all issues from github organization org

        @param org str: organization name.
        """
        git_host_name = "github"
        org = self.api.get_organization(org)
        repos = fetchall_from_paginated_list(org.get_repos())
        repos = [rep.full_name for rep in repos]
        self.pool.starmap(self.getIssuesFromGithubRepo, zip(itertools.repeat(git_host_name), repos))

    def getIssuesFromGithubOrganizations(self, *orgs):
        """
        Populates all issues from github organizations list orgs.

        @param orgs list[str]: list of organizations names.
        """
        git_host_name = "github"
        self.pool.starmap(self.getIssuesFromGithubOrganization, zip(itertools.repeat(git_host_name), orgs))

    def getReposFromGithubOrgs(self, *orgs):
        """
        Populate repos models from list of organizations names.

        @param orgs list[str]: list of organizations names.

        """
        git_host_name = "github"
        self.pool.starmap(self.getReposFromGithubOrg, zip(itertools.repeat(git_host_name), orgs))

    def getReposFromGithubOrg(self, org):
        """
        Populates repos from organization.

        @param org str: organization names.

        """
        git_host_name = "github"
        org = self.api.get_organization(org)
        repos = fetchall_from_paginated_list(org.get_repos())

        def process_repo_from_github(repo):
            """
            Process issue from github issue.

            @param issue Issue: issue object.
            """
            labels = fetchall_from_paginated_list(repo.get_labels())
            milestones = fetchall_from_paginated_list(repo.get_milestones())
            issues = fetchall_from_paginated_list(repo.get_issues())

            url = 'https://github.com/%s' % repo.full_name
            repo_model = self.repoCollection.getFromGitHostID(
                git_host_name=git_host_name, git_host_id=repo.id, git_host_url=url)

            repo_model.dbobj.name = repo.name
            repo_model.dbobj.description = repo.description or ''
            repo_model.dbobj.owner = self.users.get(repo.owner.name, '')
            repo_model.dbobj.nrIssues = len(issues)
            repo_model.dbobj.nrMilestones = len(milestones)
            repo_model.inGithub = True
            repo_model.changed = True
            repo_model.save()

            self.repos[repo.full_name] = repo_model.key
        pool = Pool(50)
        pool.map(process_repo_from_github, repos)

    # def getRepoFromGithubRepo(self, git_host_name, repo):
    #     """
    #     Populate repo model from github repository.
    #
    #     @param repo str: repository name.
    #     """
    #
    #
    #     repoid = repo.id
    #     labels = fetchall_from_paginated_list(repo.get_labels())
    #     milestones = fetchall_from_paginated_list(repo.get_milestones())
    #
    #     url = "https://github.com/%s" % repo
    #     repo_model = self.repoCollection.getFromGitHostID(git_host_name=git_host_name, git_host_id=repoid, git_host_url=url)
    #     # repo_model.dbobj.labels = [lbl.name for lbl in labels]
    #
    #
    #     # HOW TO CALCULATE THE MEMBERS OF REPO? or should check the members of the team in it's parent org?
    #     members = []
    #     repoorg = repo.organization
    #     if repoorg.name is not None:
    #         members = fetchall_from_paginated_list(repoorg.get_members())
    #     repo_model.dbobj.members = []
    #     for member in members:
    #         member_scheme = j.data.capnp.getMemoryObj(repo_model._capnp_schema.Member, userKey=str(member.id), access=0)
    #         repo_model.dbobj.members.append(member_scheme)

        # repo_model.dbobj.milestones = []
        # for milestone in milestones:
        #     nrclosedissues = milestone.closed_issues
        #     nropenissues = milestone.open_issues
        #     nrallissues = nropenissues + nrclosedissues
        #     ncomplete = 100
        #     if nrallissues>0:
        #         ncomplete = int(100*nrclosedissues/nrallissues)
        #     md = {
        #         "name": milestone.title,
        #         "id": milestone.id,
        #         "deadline": githubtimetoint(milestone.due_on),
        #         "isClosed": milestone.state!="open",
        #         "nrIssues": nropenissues + nrclosedissues,
        #         "nrClosedIssues": nrclosedissues,
        #         "completeness" : ncomplete #ceil(nrClosedIssuesForThisMilestone/); #in integer (0-100)
        #     }
        #     milestone_scheme = j.data.capnp.getMemoryObj(repo_model._capnp_schema.Milestone, **md)
        #     milestone_scheme.id = milestone.id
        #     repo_model.dbobj.milestones.append(milestone_scheme)

        # repo_model.dbobj.name = repo.name
        # repo_model.dbobj.description = repo.name
        # repo_model.dbobj.nrIssues = len(repo.issues)
        # repo_model.dbobj.nrMilestones = len(milestones)
        # repo_model.dbobj.inGithub = True
        # repo_model.save()

    def syncAllFromGithub(self, *orgs):
        self.getUsersFromGithubOrgs(*orgs)
        self.getOrgsFromGithub(*orgs)
        self.getReposFromGithubOrgs(*orgs)
        self.getIssuesFromGithubOrganizations(*orgs)
