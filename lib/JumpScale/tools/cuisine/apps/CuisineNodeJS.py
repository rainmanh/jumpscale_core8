from JumpScale import j

app = j.tools.cuisine._getBaseAppClass()


class CuisineNodeJS(app):
    NAME = 'nodejs'

    def __init__(self, executor, cuisine):
        self._executor = executor
        self._cuisine = cuisine
        self._bowerDir = ""

    @property
    def npm(self):
        return self._cuisine.core.args_replace('$binDir/npm')

    def bowerInstall(self, name):
        if self._bowerDir == "":
            self.install()
            self._cuisine.core.dir_ensure("$tmpDir/bower")
            self._bowerDir = self._cuisine.core.args_replace("$tmpDir/bower")
        if j.data.types.list.check(name):
            for item in name:
                self.bowerInstall(item)
        else:
            print("bower install %s" % name)
            self._cuisine.core.run("cd %s;bower install %s" % (self._bowerDir, name))

    def install(self, reset=False):
        """
        """
        # version = "6.9.2"
        version = "7.2.1"
        if reset == False and self._cuisine.core.file_exists('$binDir/npm'):
            return

        if self._cuisine.core.isMac:
            url = 'https://nodejs.org/dist/v%s/node-v%s-darwin-x64.tar.gz' % (version, version)
        elif self._cuisine.core.isUbuntu:
            url = 'https://nodejs.org/dist/v%s/node-v%s-linux-x64.tar.xz' % (version, version)

        else:
            raise j.exceptions.Input(message="only support ubuntu & mac", level=1, source="", tags="", msgpub="")

        cdest = self._cuisine.core.file_download(url, expand=True, overwrite=False, to="$tmpDir")

        # copy file to correct locations.
        self._cuisine.core.dir_ensure('$binDir')
        self._cuisine.core.dir_ensure('$appDir/npm')
        src = '%s/bin/node' % cdest
        self._cuisine.core.file_copy(src, '$binDir', recursive=True, overwrite=True)
        src = '%s/lib/node_modules/npm/*' % cdest
        self._cuisine.core.file_copy(src, '$appDir/npm', recursive=True, overwrite=True)
        if self._cuisine.core.file_exists('$binDir/npm'):
            self._cuisine.core.file_unlink('$binDir/npm')
        self._cuisine.core.file_link('$appDir/npm/cli.js', '$binDir/npm')

        self._cuisine.core.run("%s install -g bower" % self.npm)
