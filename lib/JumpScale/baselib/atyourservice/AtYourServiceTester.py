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
        self.aysrepo.destroy(uninstall=False)

    def gitpull(self,message="unknown"):
        self.reset()
        self.git.commit(message)
        self.git.pull()

    def gitpush(self,message="unknown"):
        self.reset()
        self.git.commit(message)
        self.git.pull()
        self.git.push()


    def doall(self):
        self.gitpull()
        self.test_init()
        self.test_install()
        self.test_change_1template_method()
        self.test_change_1template_schema()
        self.test_change_blueprint()
        self.test_change_instancehrd()


    def test_init(self):
        if self.subname!="main":
            raise j.exceptions.Input("test only supported on main")        
        #test basic init
        #ask for simulation first, check that the ays will be done in right order (using the producers)
        #check that some required aysi are there (do some finds)
        # some other basic tests

    def test_install(self):
        if self.subname!="main":
            raise j.exceptions.Input("test only supported on main")
        #test install
        #ask for simulation first, check that the ays will be done in right order (using the producers)
        #some other basic tests


    def test_change_1template_method(self):
        if self.subname!="main":
            raise j.exceptions.Input("test only supported on main")
        #change 1 template method
        #ask for aysrun for init, check the aysrun is ok, right aysi impacted
        #do init
        #check that right ays were impacted and only the ones required (through state object)

    def test_change_1template_schema(self):
        if self.subname!="main":
            raise j.exceptions.Input("test only supported on main")
        #change 1 template schema (add variable)
        #ask for aysrun for init, check the aysrun is ok, right aysi impacted
        #do init
        #check that right ays were impacted and only the ones required (through state object)
        #do now same for remove of variable

    def test_change_blueprint(self):
        if self.subname!="main":
            raise j.exceptions.Input("test only supported on main")
        #change an argument in blueprint
        #ask for aysrun for init, check the aysrun is ok, right aysi impacted
        #do init
        #check that right ays were impacted and only the ones required (through state object)
        #do now same for additional aysi in blueprint

    def test_change_instancehrd(self):
        if self.subname!="main":
            raise j.exceptions.Input("test only supported on main")
        #change hrd for 1 instance
        #ask for aysrun for init, check the aysrun is ok, right aysi impacted
        #do init
        #check that right ays were impacted and only the ones required (through state object)

        #result should be that the install action is changed




