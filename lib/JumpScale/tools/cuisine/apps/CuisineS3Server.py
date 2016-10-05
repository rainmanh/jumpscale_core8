from JumpScale import j
from time import sleep


app = j.tools.cuisine._getBaseAppClass()


class CuisineS3Server(app):
    NAME = 's3server'

    def __init__(self, executor, cuisine):
        self._executor = executor
        self._cuisine = cuisine

    def _build(self):
        # TODO: *1
        # build
        raise NotImplementedError

    def install(self, start=False, storageLocation=""):
        """
        put backing store on /storage/...
        """
        path = self._cuisine.development.git.pullRepo('https://github.com/scality/S3.git')
        self._cuisine.core.run('cd {} && npm install'.format(path))

        # TODO: *1 copy files back to $appDir/s3server
        # TODO: *1 storage location configuration

        if start:
            self.start()

    def start(self, name=NAME):
        path = j.sal.fs.joinPaths(j.dirs.codeDir, 'github', 'scality', 'S3')
        self._cuisine.core.run('cd {} && npm start'.format(path))

    def test(self):
        # put/get file over S3 interface using a python S3 lib
        pass
