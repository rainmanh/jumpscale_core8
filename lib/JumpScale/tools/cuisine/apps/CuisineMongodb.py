from JumpScale import j
from time import sleep


app = j.tools.cuisine._getBaseAppClass()


class CuisineMongodb(app):
    NAME = 'mongod'

    def _build(self, reset=False):
        if reset and self.cuisine.core.isMac:
            self.cuisine.core.run("brew uninstall mongodb", die=False)
        if not reset and self.isInstalled():
            self.log('MongoDB is already installed.')
            return
        else:
            appbase = "%s/" % self.cuisine.core.dir_paths["BINDIR"]
            self.cuisine.core.dir_ensure(appbase)

            url = None
            if self.cuisine.core.isUbuntu:
                # TODO: *2 upgrade ubuntu
                # https://fastdl.mongodb.org/linux/mongodb-linux-x86_64-ubuntu1604-3.4.0.tgz
                url = 'https://fastdl.mongodb.org/linux/mongodb-linux-x86_64-ubuntu1604-3.2.9.tgz'
            elif self.cuisine.core.isArch:
                self.cuisine.package.install("mongodb")
            elif self.cuisine.core.isMac:  # TODO: better platform mgmt
                url = 'https://fastdl.mongodb.org/osx/mongodb-osx-ssl-x86_64-3.4.0.tgz'
            else:
                raise j.exceptions.RuntimeError("unsupported platform")

            if url:
                self.log('Downloading mongodb.')
                self.cuisine.core.file_download(url, to="$TMPDIR", overwrite=False, expand=True)
                tarpath = self.cuisine.core.find("$TMPDIR", recursive=True, pattern="*mongodb*.tgz", type='f')[0]
                self.cuisine.core.file_expand(tarpath, "$TMPDIR")
                extracted = self.cuisine.core.find("$TMPDIR", recursive=True, pattern="*mongodb*", type='d')[0]
                for file in self.cuisine.core.find('%s/bin/' % extracted, type='f'):
                    self.cuisine.core.file_copy(file, appbase)

    def install(self, start=True, name='mongod'):
        """
        download, install, move files to appropriate places, and create relavent configs
        """
        self.cuisine.core.dir_ensure('$VARDIR/data/%s' % name)
        if start:
            self.start(name)

    def build(self, start=True, install=True, reset=False):
        self._build(reset=reset)
        if install:
            self.install(start)

    def start(self, name="mongod"):
        which = self.cuisine.core.command_location("mongod")
        self.cuisine.core.dir_ensure('$VARDIR/data/%s' % name)
        cmd = "%s --dbpath $VARDIR/data/%s" % (which, name)
        # self.cuisine.process.kill("mongod")
        self.cuisine.processmanager.ensure(name, cmd=cmd, env={}, path="")

    def stop(self, name='mongod'):
        self.cuisine.processmanager.stop(name)
