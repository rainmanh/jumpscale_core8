from JumpScale import j
from time import sleep


app = j.tools.cuisine._getBaseAppClass()


class CuisineMongodb(app):
    NAME = 'mongod'

    def __init__(self, executor, cuisine):
        self._executor = executor
        self._cuisine = cuisine

    def _build(self):
        if self.isInstalled():
            print('MongoDB is already installed.')
            return
        else:
            appbase = "%s/" % self._cuisine.core.dir_paths["binDir"]
            self._cuisine.core.dir_ensure(appbase)

            url = None
            if self._cuisine.core.isUbuntu:
                url = 'https://fastdl.mongodb.org/linux/mongodb-linux-x86_64-ubuntu1604-3.2.9.tgz'
            elif self._cuisine.core.isArch:
                self._cuisine.package.install("mongodb")
            elif self._cuisine.core.isMac:  # TODO: better platform mgmt
                url = 'https://fastdl.mongodb.org/osx/mongodb-osx-x86_64-3.2.1.tgz'
            else:
                from IPython import embed
                print("DEBUG NOW sds")
                embed()
                raise RuntimeError("stop debug here")
                raise RuntimeError("unsupported platform")
                return

            if url:
                print('Downloading mongodb.')
                self._cuisine.core.file_download(url, to="$tmpDir", overwrite=False, expand=True)
                tarpath = self._cuisine.core.fs_find("$tmpDir", recursive=True, pattern="*mongodb*.tgz", type='f')[0]
                self._cuisine.core.file_expand(tarpath, "$tmpDir")
                extracted = self._cuisine.core.fs_find("$tmpDir", recursive=True, pattern="*mongodb*", type='d')[0]
                for file in self._cuisine.core.fs_find('%s/bin/' % extracted, type='f'):
                    self._cuisine.core.file_copy(file, appbase)

    def install(self, start=True, name='mongod'):
        """
        download, install, move files to appropriate places, and create relavent configs
        """
        self._cuisine.core.dir_ensure('$varDir/data/%s' % name)
        if start:
            self.start(name)

    def build(self, start=True, install=True):
        self._build()
        if install:
            self.install(start)

    def start(self, name="mongod"):
        which = self._cuisine.core.command_location("mongod")
        self._cuisine.core.dir_ensure('$varDir/data/%s' % name)
        cmd = "%s --dbpath $varDir/data/%s" % (which, name)
        # self._cuisine.process.kill("mongod")
        pm = self._cuisine.processmanager.get("tmux")
        pm.ensure(name, cmd=cmd, env={}, path="")

    def stop(self, name='mongod'):
        self._cuisine.processmanager.stop(name)
