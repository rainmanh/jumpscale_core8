from JumpScale import j
from JumpScale.tools.zip.ZipFile import ZipFile

from Repository import GithubRepo
from User import User
from Milestone import RepoMilestone

try:
    import github
except:
    cmd = "pip3 install pygithub"
    j.do.execute(cmd)
    import github


class GitHubFactory(object):

    def __init__(self):
        self.__jslocation__ = "j.clients.github"

    # def getRepoClient(self, account, reponame):
    #     return GitHubRepoClient(account, reponame)

    def getClient(self, secret):
        return GitHubClient(secret)


class GitHubClient():

    def __init__(self, secret):
        self.api = github.Github(secret)
        self.users = {}
        self._milestones = {}

    def getRepo(self, fullname):
        """
        fullname e.g. incubaid/myrepo
        """
        return GithubRepo(self, fullname)

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

    def getMilestone(self, number=None, githubObj=None):
        if number in self._milestones:
            return self._milestones[number]

        if githubObj is not None:
            if githubObj.number not in self._milestones:
                obj = RepoMilestone(self, githubObj=githubObj)
                self._milestones[githubObj.number] = obj
            return self._milestones[githubObj.number]
