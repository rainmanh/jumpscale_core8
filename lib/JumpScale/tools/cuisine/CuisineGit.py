
from JumpScale import j

class CuisineGit():
    def __init__(self,executor,cuisine):
        self.executor=executor
        self.cuisine=cuisine


    def pullRepo(self,url,dest=None,login="",passwd=None,depth=1,\
            ignorelocalchanges=True,reset=False,branch=None,revision=None, ssh="first"):        

        if dest==None:
            base,provider,account,repo,dest,url=j.do.getGitRepoArgs(url,dest,login,passwd,reset=reset, ssh=ssh,codeDir=self.cuisine.core.dir_paths["codeDir"])
            #we need to work in remote linux so we only support /opt/code
        else:
            dest = self.cuisine.core.args_replace(dest)


        git_cli = j.clients.github.getClient(login, url, branch, self.executor)

        return git_cli.pullGitRepo(url=url,dest=dest,login=login,passwd=passwd,depth=depth,\
            ignorelocalchanges=ignorelocalchanges,reset=reset,branch=branch,revision=revision, ssh=ssh)

