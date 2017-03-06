from JumpScale import j

app = j.tools.cuisine._getBaseAppClass()


class CuisineNodeJS(app):
    NAME = 'nodejs'

    def _init(self):
        self._bowerDir = ""

    @property
    def npm(self):
        return self.replace('$BASEDIR/node/bin/npm')

    @property
    def NODE_PATH(self):
        return self.replace('$BASEDIR/node/lib/node_modules')

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
            self.logger.info("bower install %s" % name)
            self.cuisine.core.run("cd %s;bower --allow-root install  %s" % (self._bowerDir, name), profile=True)

    def install(self, reset=False):
        """
        """
        if not reset and self.doneGet("install"):
            return

        self.cuisine.core.file_unlink("$BINDIR/node")
        self.cuisine.core.dir_remove("$JSAPPSDIR/npm")

        version = "7.7.1"
        if reset == False and self.cuisine.core.file_exists('$BINDIR/npm'):
            return

        if self.cuisine.core.isMac:
            url = 'https://nodejs.org/dist/v%s/node-v%s-darwin-x64.tar.gz' % (version, version)
        elif self.cuisine.core.isUbuntu:
            url = 'https://nodejs.org/dist/v%s/node-v%s-linux-x64.tar.gz' % (version, version)

        else:
            raise j.exceptions.Input(message="only support ubuntu & mac", level=1, source="", tags="", msgpub="")

        cdest = self.cuisine.core.file_download(url, expand=True, overwrite=False, to="$TMPDIR")

        # copy file to correct locations.
        self.cuisine.core.dir_ensure('$BASEDIR/node/npm')
        self.cuisine.core.dir_ensure('$BASEDIR/node/bin')
        self.cuisine.core.dir_ensure(self.NODE_PATH)
        src = '%s/bin/node' % cdest
        self.cuisine.core.file_copy(src, '$BASEDIR/node/bin/', recursive=True, overwrite=True)
        src = '%s/lib/node_modules/npm/*' % cdest
        self.cuisine.core.file_copy(src, '$BASEDIR/node/npm', recursive=True, overwrite=True)
        if self.cuisine.core.file_exists('$BASEDIR/node/bin/npm'):
            self.cuisine.core.file_unlink('$BASEDIR/node/bin/npm')
        self.cuisine.core.file_link('$BASEDIR/node/npm/cli.js', '$BASEDIR/node/bin/npm')

        for item in self.cuisine.bash.profileDefault.paths:
            if "node" in item or "npm" in item:
                self.logger.info("remove %s from path in default profile." % item)
                self.cuisine.bash.profileDefault.pathDelete(item)

        for item in self.cuisine.bash.profileJS.paths:
            if "node" in item or "npm" in item:
                self.logger.info("remove %s from path in default profile." % item)
                self.cuisine.bash.profileDefault.pathDelete(item)

        self.cuisine.bash.profileDefault.envSet("NODE_PATH", self.NODE_PATH)
        self.cuisine.bash.profileDefault.addPath(self.cuisine.core.replace("$BASEDIR/node/bin/"))
        self.cuisine.bash.profileDefault.save()

        rc, out, err = self.cuisine.core.run("npm -v")

        assert out == '4.1.2'  # needs to be this version because is part of the package which was downloaded

        rc, initmodulepath, err = self.cuisine.core.run("%s config get init-module" % self.npm)
        self.cuisine.core.file_unlink(initmodulepath)
        self.cuisine.core.run("%s config set global true -g" % self.npm)
        self.cuisine.core.run(self.replace("%s config set init-module $BASEDIR/node/.npm-init.js -g" % self.npm))
        self.cuisine.core.run(self.replace("%s config set init-cache $BASEDIR/node/.npm -g" % self.npm))
        self.cuisine.core.run("%s config set global true " % self.npm)
        self.cuisine.core.run(self.replace("%s config set init-module $BASEDIR/node/.npm-init.js " % self.npm))
        self.cuisine.core.run(self.replace("%s config set init-cache $BASEDIR/node/.npm " % self.npm))
        self.cuisine.core.run("%s install -g bower" % self.npm, profile=True, shell=True)

        self.cuisine.core.run("%s install npm@latest -g" % self.npm)

        self.doneSet("install")
