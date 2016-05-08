from JumpScale import j

import colored_traceback
colored_traceback.add_hook(always=True)

class AtYourServiceTester():

    def __init__(self,subname="main"):

        self.subname=subname
        self.basepath=j.sal.fs.joinPaths(j.dirs.codeDir,"github","jumpscale","jumpscale_ays8_testenv",subname)

        #checkout a prepared ays test repo with some special ays templates to test behaviour & easy to check outcome
        if not j.sal.fs.exists(self.basepath):
            url="git@github.com:Jumpscale/jumpscale_ays8_testenv.git"
            repo=j.do.pullGitRepo(url)

        self._git=None

        self.aysrepo=j.atyourservice.get(self.basepath)
        
    @property    
    def git(self):
        if self._git==None:
            self._git=j.clients.git.get(self.basepath)
        return self._git

    def reset(self):
        self.aysrepo.destroy()

    def gitpull(self):
        self.reset()
        self.git.pull()

    def gitpush(self):
        self.reset()
        from IPython import embed
        print ("DEBUG NOW commit")
        embed()
        
        self.git.push()


    def doall(self):
        from IPython import embed
        print ("DEBUG NOW test doall")
        embed()
        
