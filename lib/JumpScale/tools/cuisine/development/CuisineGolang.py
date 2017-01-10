
from JumpScale import j
# import os


app = j.tools.cuisine._getBaseAppClass()


class CuisineGolang(app):

    NAME = 'go'

    def isInstalled(self):
        rc, out, err = self.cuisine.core.run("go version", die=False, showout=False, profile=True)
        if rc > 0 or "1.7.4" not in out:
            return False
        if self.doneGet("install")==False:
            return False
        return True

    def install(self, reset=False):
        if reset is False and self.isInstalled():
            return
        if self.cuisine.core.isMac:
            downl = "https://storage.googleapis.com/golang/go1.7.4.darwin-amd64.tar.gz"
        elif "ubuntu" in self.cuisine.platformtype.platformtypes:
            downl = "https://storage.googleapis.com/golang/go1.7.4.linux-amd64.tar.gz"
        else:
            raise j.exceptions.RuntimeError("platform not supported")

        GOROOTDIR = self.cuisine.core.dir_paths['GOROOTDIR']
        GOPATHDIR = self.cuisine.core.dir_paths['GOPATHDIR']

        self.cuisine.core.run(cmd="rm -rf $GOROOTDIR", die=False)

        profile = self.cuisine.bash.profileDefault
        profile.envSet("GOROOT", GOROOTDIR)
        profile.envSet("GOPATH", GOPATHDIR)
        profile.addPath(self.cuisine.core.joinpaths(GOPATHDIR, 'bin'))
        profile.addPath(self.cuisine.core.joinpaths(GOROOTDIR, 'bin'))
        profile.save()

        self.cuisine.core.file_download(downl, GOROOTDIR, overwrite=False, retry=3, timeout=0, expand=True, removeTopDir=True)

        self.cuisine.core.dir_ensure("%s/src" % GOPATHDIR)
        self.cuisine.core.dir_ensure("%s/pkg" % GOPATHDIR)
        self.cuisine.core.dir_ensure("%s/bin" % GOPATHDIR)

        self.get("github.com/tools/godep")
        self.goraml()

        self.doneSet("install")

    def goraml(self):
        C = '''
        go get -u github.com/Jumpscale/go-raml
        set -ex
        go get -u github.com/jteeuwen/go-bindata/...
        cd $GOPATH/src/github.com/jteeuwen/go-bindata/go-bindata
        go build
        go install
        cd $GOPATH/src/github.com/Jumpscale/go-raml
        sh build.sh
        '''
        self.cuisine.core.execute_bash(C, profile=True)

    def glide(self):
        """
        install glide
        """
        if self.doneGet('glide'):
            return
        self.cuisine.core.file_download('https://glide.sh/get', '$TMPDIR/installglide.sh', minsizekb=4)
        self.cuisine.core.run('. $TMPDIR/installglide.sh', profile=True)
        self.doneSet('glide')

    @property
    def GOPATH(self):
        return self.cuisine.core.dir_paths["GOPATHDIR"]

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
        GOPATH = self.cuisine.bash.env['GOPATH']

        pullurl = "git@%s.git" % url.replace('/', ':', 1)

        dest = self.cuisine.development.git.pullRepo(pullurl,
                                                     branch=branch,
                                                     depth=depth,
                                                     dest='%s/src/%s' % (GOPATH, url),
                                                     ssh=False)
        self.cuisine.core.run('cd %s && godep restore' % dest, profile=True)
