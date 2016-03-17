from JumpScale import j


from ActionDecorator import ActionDecorator


"""
please ensure that the start and build methods are separate and
the build doesnt place anyfile outside opt as it will be used in aysfs mounted system
"""


class actionrun(ActionDecorator):
    def __init__(self, *args, **kwargs):
        ActionDecorator.__init__(self, *args, **kwargs)
        self.selfobjCode = "cuisine=j.tools.cuisine.getFromId('$id');selfobj=cuisine.apps.mongodb"


class Mongodb():

    def __init__(self, executor, cuisine):
        self.executor = executor
        self.cuisine = cuisine

    @actionrun(action=True)
    def build(self, start=True):
        self.cuisine.installer.base()
        exists = self.cuisine.core.command_check("mongod")

        if exists:
            cmd = self.cuisine.core.command_location("mongod")
            dest = "%s/mongod" % self.cuisine.core.dir_paths["binDir"]
            if j.sal.fs.pathClean(cmd) != j.sal.fs.pathClean(dest):
                self.cuisine.core.file_copy(cmd, dest)
        else:
            appbase = self.cuisine.core.dir_paths["binDir"]

            url = None
            if self.cuisine.core.isUbuntu:
                url = 'https://fastdl.mongodb.org/linux/mongodb-linux-x86_64-ubuntu1404-3.2.1.tgz'
            elif self.cuisine.core.isArch:
                self.cuisine.package.install("mongodb")
            elif self.cuisine.core.isMac:  # @todo better platform mgmt
                url = 'https://fastdl.mongodb.org/osx/mongodb-osx-x86_64-3.2.1.tgz'
            else:
                raise RuntimeError("unsupported platform")
                return

            if url:
                self.cuisine.core.file_download(url, to="$tmpDir", overwrite=False, expand=True)
                tarpath = self.cuisine.core.fs_find("$tmpDir", recursive=True, pattern="*mongodb*.tgz", type='f')[0]
                self.cuisine.core.file_expand(tarpath, "$tmpDir")
                extracted = self.cuisine.core.fs_find("$tmpDir", recursive=True, pattern="*mongodb*", type='d')[0]
                for file in self.cuisine.core.fs_find('%s/bin/' % extracted, type='f'):
                    self.cuisine.core.file_copy(file, appbase)

        self.cuisine.core.dir_ensure('$varDir/data/mongodb')

        if start:
            self.start("mongod")

    def start(self, name="mongod"):
        which = self.cuisine.core.command_location("mongod")
        self.cuisine.core.dir_ensure('$varDir/data/mongodb')
        cmd = "%s --dbpath $varDir/data/mongodb" % which
        self.cuisine.process.kill("mongod")
        self.cuisine.processmanager.ensure("mongod", cmd=cmd, env={}, path="")
