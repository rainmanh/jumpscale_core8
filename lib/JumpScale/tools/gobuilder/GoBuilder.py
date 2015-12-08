from JumpScale import j
import os
import urllib.parse


class GoBuilder(object):
    """docstring for GoBuilder"""
    def __init__(self):
        super(GoBuilder, self).__init__()
        self._gopath = None
        self._env = os.environ
        self.executor = j.tools.executor.getLocal()

    @property
    def gopath(self):
        return self._gopath

    @gopath.setter
    def gopath(self, value):
        self._gopath = value.rstrip("/")
        self._env['GOPATH'] = self._gopath
        self._env['PATH'] = '%s:%s/bin' % (self._env['PATH'], self._gopath)

    def createGOPATH(self, path):
        """
        create GOPATH directry structure and set the gopath attributes
        """
        gopath_dir = j.tools.path.get(path)
        if not gopath_dir.exists():
            gopath_dir.mkdir(551)
            j.tools.path.get(gopath_dir.join('pkg')).mkdir_p(551)
            j.tools.path.get(gopath_dir.join('src')).mkdir_p(551)
            j.tools.path.get(gopath_dir.join('bin')).mkdir_p(551)

        self.gopath = path.rstrip("/")
        self._env['PATH'] = '%s:%s/bin' % (self._env['PATH'], self.gopath)

    def buildProject(self, package=None, generate=False):
        """
        build a project using go get
        @package : package name
        @generate: boolean, if True, go generate is called in build process
        """
        if package is None:
            j.events.inputerror_critical(msg="package can't be none", category="go build", msgpub='')

        if self.gopath is None:
            j.events.inputerror_critical(msg="gopath can't be none", category="go build", msgpub='')

        getcmd = 'go get -a -u -v %s' % package
        generatecmd = 'go generate %s' % package
        re, out, err = 0, '', ''

        if generate:
            print("start : %s" % generate)
            rc, out = self.executor.execute(generatecmd)
            print("go generate succeed" if rc == 0 else "error during go generate")

        print("start : %s" % getcmd)
        rc, out = self.executor.execute(getcmd)
        print("go get succeed" if rc == 0 else "error during go get")

    def buildProjectGodep(self, packageURL=None, generate=False, aptDeps=[]):
        """
        build a project using godep
        @package : url of the git repo of the project
        @generate: boolean, if True, go generate is called in build process
        """
        if packageURL is None:
            j.events.inputerror_critical(msg="package can't be none", category="go build", msgpub='')

        if self.gopath is None:
            j.events.inputerror_critical(msg="gopath can't be none", category="go build", msgpub='')

        url = urllib.parse.urlparse(packageURL)

        gopath = j.tools.path.get(self.gopath)
        godepbin = gopath.joinpath('bin', 'godep')

        dest = gopath.joinpath('src', "%s%s" %(url.hostname, url.path))

        if dest.exists():
            j.tools.path.get(dest).rmtree()

        cmds = [
            'apt-get install -y %s' % ' '.join(aptDeps),
            'go get -u -v github.com/tools/godep',
            'git clone %s %s' % (packageURL, dest),
            'cd %s && %s restore' % (dest, godepbin),
        ]
        if generate:
            cmds.append('cd %s && %s go generate' % (dest, godepbin))
        cmds.append('cd %s && %s go install' % (dest, godepbin))

        for cmd in cmds:
            print("start: %s" % cmd)
            rc, out = self.executor.execute(cmd)
            if rc != 0:
                raise RuntimeError('Failed to execute %s - (%s, %s, %s)' % (cmd, re, out, err))

            print("%s: succeed" % cmd if rc == 0 else "%s: error" % cmd)

    def deleteGOPATH(self, serviceObj):
        if self.gopath:
            gopath = j.tools.path.get(self.gopath).removedirs_p()
