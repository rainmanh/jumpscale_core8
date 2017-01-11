from JumpScale import j
import os
import textwrap

app = j.tools.cuisine._getBaseAppClass()


class CuisineGogs(app):
    NAME = "gogs"

    def _init(self):
        self._gogspath = str()
        self._gopath = str()
        self._appini = str()
        self.BUILDDIR = self.gogspath
        self.CODEDIR = self.gogspath

    @property
    def gopath(self):
        if not self._gopath:
            self._gopath = self.cuisine.development.golang.GOPATH
            return self._gopath
        else:
            return self._gopath

    @property
    def gogspath(self):
        if not self._gogspath:
            self._gogspath = os.path.join(self.gopath, "src", "github.com", "gogits", "gogs")
            return self._gogspath
        else:
            return self._gogspath

    @property
    def appini(self):
        if not self._appini:
            self._appini = os.path.join(self.gogspath, "custom", "conf", "app.ini")
            return self._appini
        else:
            return self._appini

    def build(self, install=True, start=True, reset=False, installDeps=False):
        # THIS IS WIP (not stable yet)
        # if reset is False and self.isInstalled():
        #     return
        # GOPATH: /optvar/go
        if self.doneGet('build') and not reset:
            return

        self.cuisine.development.golang.install()
        self.cuisine.development.golang.glide()

        self.cuisine.bash.envSet('GOGITSDIR', '%s/src/github.com/gogits' % self.gogspath )
        self.cuisine.bash.envSet('GOGSDIR', '$GOGITSDIR/gogs')

        self.cuisine.development.golang.get('golang.org/x/oauth2')
        self.cuisine.development.golang.get('github.com/gogits/gogs')

        self.cuisine.core.run('cd %s && git remote add gigforks https://github.com/gigforks/gogs' % self.gogspath,
                              profile=True)
        self.cuisine.core.run('cd %s && git fetch gigforks && git checkout gigforks/itsyouimpl' % self.gogspath,
                              profile=True, timeout=1200)
        self.cuisine.core.run('cd %s && glide install && go build -tags "sqlite cert"' % self.gogspath, profile=True,
                              timeout=1200)

        self.doneSet('build')


    def install(self):
        """
        GOGS has no files to move this method is for standardization of cuisine
        """
        pass

    def write_itsyouonlineconfig(self):
        # ADD EXTRA CUSTOM INFO FOR ITS YOU ONLINE.
        if self.doneGet('config'):
            return
        itsyouonlinesection = """\
        [itsyouonline]
        CLIENT_ID     = itsyouref
        CLIENT_SECRET = khZNlrGFiVqHb9u7h6Kh5IvZXY_aE1gWYL_v2Ike9WOZkza4j2k9
        REDIRECT_URL  = http://localhost:3000/oauth/redirect
        AUTH_URL      = https://itsyou.online/v1/oauth/authorize
        TOKEN_URL     = https://itsyou.online/v1/oauth/access_token
        SCOPE        = user:email

        """

        itsyouonlinesection = textwrap.dedent(itsyouonlinesection)
        if self.cuisine.core.file_exists(self.appini):
            self.cuisine.core.file_write(location=self.appini,
                                         content=itsyouonlinesection,
                                         append=True)
        self.doneSet('config')

    def start(self, name='main'):
        cmd = "{gogspath}/gogs web".format(gogspath=self.gogspath)
        self.cuisine.processmanager.ensure(name='gogs_%s' % name, cmd=cmd)

    def stop(self, name='main'):
        self.cuisine.processmanager.stop('gogs_%s' % name)

    def restart(self):
        self.cuisine.processmanager.stop("gogs")
        self.start()

    def reset(self):
        """
        helper method to clean what this module generates.
        """
        super().reset()
        self.core.dir_remove(self.BUILDDIR)
        self.core.dir_remove(self.CODEDIR)
