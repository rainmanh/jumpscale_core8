from JumpScale import j

app = j.tools.cuisine._getBaseAppClass()


class CuisineNodeJS(app):
    NAME = 'nodejs'

    def _init(self):
        self._bowerDir = ""

    @property
    def npm(self):
        return self.replace('$BINDIR/npm')

    def bowerInstall(self, name):
        """
        @param name can be a list or string
        """
        if self._bowerDir == "":
            self.install()
            self.cuisine.core.dir_ensure("$TMPDIR/bower")
            self._bowerDir = self.replace("$TMPDIR/bower")
        if j.data.types.list.check(name):
            for item in name:
                self.bowerInstall(item)
        else:
            self.log("bower install %s" % name)
            self.cuisine.core.run("cd %s;bower install %s" % (self._bowerDir, name))

    def install(self, reset=False):
        """
        """
        if not reset and self.doneGet("install"):
            return
        # version = "6.9.2"
        version = "7.2.1"
        if reset == False and self.cuisine.core.file_exists('$BINDIR/npm'):
            return

        if self.cuisine.core.isMac:
            url = 'https://nodejs.org/dist/v%s/node-v%s-darwin-x64.tar.gz' % (version, version)
        elif self.cuisine.core.isUbuntu:
            url = 'https://nodejs.org/dist/v%s/node-v%s-linux-x64.tar.xz' % (version, version)

        else:
            raise j.exceptions.Input(message="only support ubuntu & mac", level=1, source="", tags="", msgpub="")

        cdest = self.cuisine.core.file_download(url, expand=True, overwrite=False, to="$TMPDIR")

        # copy file to correct locations.
        self.cuisine.core.dir_ensure('$BINDIR')
        self.cuisine.core.dir_ensure('$JSAPPSDIR/npm')
        src = '%s/bin/node' % cdest
        self.cuisine.core.file_copy(src, '$BINDIR', recursive=True, overwrite=True)
        src = '%s/lib/node_modules/npm/*' % cdest
        self.cuisine.core.file_copy(src, '$JSAPPSDIR/npm', recursive=True, overwrite=True)
        if self.cuisine.core.file_exists('$BINDIR/npm'):
            self.cuisine.core.file_unlink('$BINDIR/npm')
        self.cuisine.core.file_link('$JSAPPSDIR/npm/cli.js', '$BINDIR/npm')

        self.cuisine.core.run("%s install -g bower" % self.npm)

        self.doneSet("install")
