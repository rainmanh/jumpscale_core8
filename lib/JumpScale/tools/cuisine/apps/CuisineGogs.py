from JumpScale import j
import os
import textwrap

app = j.tools.cuisine._getBaseAppClass()


class CuisineGogs(app):
    NAME = "gogs"

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.gopath = self._cuisine.bash.environ.get('GOPATH')
        self.gogspath = os.path.join(self.gopath, "src", "github.com", "gogits", "gogs")
        self.appini = os.path.join(self.gogspath, "custom", "conf", "app.ini")

    def build(self, install=True, start=True, reset=False, installDeps=False):
        # THIS IS WIP (not stable yet)
        # if reset is False and self.isInstalled():
        #     return
        # GOPATH: /optvar/go
        if installDeps:
            self._cuisine.development.golang.install()

        script = """
        #set -xe
        . ~/.profile_js
        curl https://glide.sh/get > installglide.sh
        . installglide.sh

        GOGITSDIR=$GOPATH/src/github.com/gogits
        GOGSDIR=$GOGITSDIR/gogs

        go get golang.org/x/oauth2
        go get github.com/gogits/gogs

        cd $GOGSDIR && git remote add xmonorigin https://github.com/xmonader/gogs-itsyouonline && git fetch xmonorigin && git checkout xmonorigin/rebranding

        cd $GOGSDIR && glide install && go build -tags "sqlite cert"
        echo **OK**

        """
        # BUILD GOGS WITH SQLITE3 tags
        rc, out = self._cuisine.core.execute_bash(script)
        if rc != 0:
            raise RuntimeError("Couldn't build gogs.")

    def write_itsyouonlineconfig(self):
        # ADD EXTRA CUSTOM INFO FOR ITS YOU ONLINE.
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
        if self._cuisine.core.file_exists(self.appini):
            self._cuisine.core.file_write(location=self.appini,
                                          content=itsyouonlinesection,
                                          append=True)

    def start(self):
        pm = self._cuisine.processmanager.get("tmux")
        cmd = "{gogspath}/gogs web".format(gogspath=self.gogspath)
        pm.ensure(name='gogs', cmd=cmd)

    def restart(self):
        self._cuisine.processmanager.stop("gogs")
        self.start()
