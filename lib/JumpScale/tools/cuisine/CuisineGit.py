
from JumpScale import j

from ActionDecorator import ActionDecorator


class actionrun(ActionDecorator):

    def __init__(self, *args, **kwargs):
        ActionDecorator.__init__(self, *args, **kwargs)
        self.selfobjCode = "cuisine=j.tools.cuisine.getFromId('$id');selfobj=cuisine.git"


base = j.tools.cuisine.getBaseClass()


class CuisineGit(base):

    def __init__(self, executor, cuisine):
        self._executor = executor
        self._cuisine = cuisine

    
    def pullRepo(self, url, dest=None, login=None, passwd=None, depth=1,
                 ignorelocalchanges=True, reset=False, branch=None, revision=None, ssh="first"):

        if dest == None:
            base, provider, account, repo, dest, url = j.do.getGitRepoArgs(
                url, dest, login, passwd, reset=reset, ssh=ssh, codeDir=self._cuisine.core.dir_paths["codeDir"])
            # we need to work in remote linux so we only support /opt/code
        else:
            dest = self._cuisine.core.args_replace(dest)

        self._cuisine.core.dir_ensure(dest)
        self._cuisine.core.dir_ensure('$homeDir/.ssh')
        keys = self._cuisine.core.run("ssh-keyscan -H github.com")[1]
        self._cuisine.core.dir_ensure('$homeDir/.ssh')
        self._cuisine.core.file_append("$homeDir/.ssh/known_hosts", keys)
        self._cuisine.core.file_attribs("$homeDir/.ssh/known_hosts", mode=600)

        return j.do.pullGitRepo(url=url, dest=dest, login=login, passwd=passwd, depth=depth,
                                ignorelocalchanges=ignorelocalchanges, reset=reset, branch=branch, revision=revision, ssh=ssh, executor=self._executor)

        self._cuisine.reset_actions()
