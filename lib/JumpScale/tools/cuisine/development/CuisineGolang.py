
from JumpScale import j
# import os


app = j.tools.cuisine._getBaseAppClass()


class CuisineGolang(app):

    NAME = 'go'

    def isInstalled(self):
        rc, out, err = self.cuisine.core.run("go version", die=False, showout=False, profile=True)
        if rc > 0 or "1.6" not in out:
            return False
        return True

    def install(self, reset=False):
        if reset is False and self.isInstalled():
            return
        if self.cuisine.core.isMac or self.cuisine.core.isArch:
            self.cuisine.core.run(cmd="rm -rf /usr/local/go", die=False)
            self.cuisine.package.install("go")
        elif "ubuntu" in self.cuisine.platformtype.platformtypes:
            downl = "https://storage.googleapis.com/golang/go1.7.1.linux-amd64.tar.gz"
            self.cuisine.core.file_download(downl, "/usr/local", overwrite=False, retry=3, timeout=0, expand=True)
        else:
            raise j.exceptions.RuntimeError("platform not supported")

        goDir = self.cuisine.core.dir_paths['GODIR']
        self.cuisine.bash.environSet("GOPATH", goDir)

        if self.cuisine.core.isMac:
            self.cuisine.bash.environSet("GOROOT", '/usr/local/opt/go/libexec/')
            self.cuisine.bash.addPath("/usr/local/opt/go/libexec/bin/")
        else:
            self.cuisine.bash.environSet("GOROOT", '/usr/local/go')
            self.cuisine.bash.addPath("/usr/local/go/bin/")

        self.cuisine.bash.addPath(self.cuisine.core.joinpaths(goDir, 'bin'))

        self.cuisine.core.dir_ensure("%s/src" % goDir)
        self.cuisine.core.dir_ensure("%s/pkg" % goDir)
        self.cuisine.core.dir_ensure("%s/bin" % goDir)

    def goraml(self):
        C = '''
        go get -u github.com/Jumpscale/go-raml
        set -ex
        cd $GOPATH/src/github.com/jteeuwen/go-bindata/go-bindata
        go build
        go install
        cd $GOPATH/src/github.com/Jumpscale/go-raml
        sh build.sh
        '''
        self.cuisine.core.execute_bash(C, profile=True)

    def install_godep(self):
        self.get("github.com/tools/godep")

    @property
    def GOPATH(self):
        return self.cuisine.core.dir_paths["GODIR"]
        # if self._gopath==None:
        #     # if not "GOPATH" in self.bash.environ:
        #     #     self.cuisine.installerdevelop.golang()
        #     # self._gopath=   self.bash.environ["GOPATH"]

        # return self._gopath

    def clean_src_path(self):
        srcpath = self.cuisine.core.joinpaths(self.GOPATH, 'src')
        self.cuisine.core.dir_remove(srcpath)

    def get(self, url):
        """
        e.g. url=github.com/tools/godep
        """
        self.clean_src_path()
        self.cuisine.core.run('go get -v -u %s' % url, profile=True)

    def godep(self, url, branch=None, depth=1):
        """
        e.g. url=github.com/tools/godep
        """
        self.clean_src_path()
        GOPATH = self.cuisine.bash.environ['GOPATH']

        pullurl = "git@%s.git" % url.replace('/', ':', 1)

        dest = self.cuisine.development.git.pullRepo(pullurl,
                                                     branch=branch,
                                                     depth=depth,
                                                     dest='%s/src/%s' % (GOPATH, url),
                                                     ssh=False)
        self.cuisine.core.run('cd %s && godep restore' % dest, profile=True)
