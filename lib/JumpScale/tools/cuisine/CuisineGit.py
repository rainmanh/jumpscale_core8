
from JumpScale import j

class CuisineGit:
    def __init__(self,executor,cuisine):
        self.executor=executor
        self.cuisine=cuisine


    def pullRepo(self,url,dest=None,login=None,passwd=None,depth=1,\
            ignorelocalchanges=True,reset=False,branch=None,revision=None, ssh="first"):

        if dest==None:
            base,provider,account,repo,dest,url=j.do.getGitRepoArgs(url,dest,login,passwd,reset=reset, ssh=ssh,codeDir=self.cuisine.core.dir_paths["codeDir"])
            #we need to work in remote linux so we only support /opt/code
        else:
            dest = self.cuisine.core.args_replace(dest)

        self.cuisine.core.dir_ensure(dest,force=False)
        self.cuisine.core.dir_ensure('$homeDir/.ssh')
        keys = self.cuisine.core.run("ssh-keyscan -H github.com",force=False)[1]
        self.cuisine.core.dir_ensure('$homeDir/.ssh')
        self.cuisine.core.file_append("$homeDir/.ssh/known_hosts", keys)
        self.cuisine.core.file_attribs("$homeDir/.ssh/known_hosts", mode=600)

        return j.do.pullGitRepo(url=url,dest=dest,login=login,passwd=passwd,depth=depth,\
            ignorelocalchanges=ignorelocalchanges,reset=reset,branch=branch,revision=revision, ssh=ssh,executor=self.executor)
