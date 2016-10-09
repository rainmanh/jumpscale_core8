from JumpScale import j
from time import sleep


app = j.tools.cuisine._getBaseAppClass()


class CuisineS3Server(app):
    NAME = 's3server'

    def __init__(self, executor, cuisine):
        self._executor = executor
        self._cuisine = cuisine

    def install(self, start=False, storageLocation="/data/", metaLocation="/meta/"):
        """
        put backing store on /storage/...
        """
        path = self._cuisine.development.git.pullRepo('https://github.com/scality/S3.git')
        self._cuisine.core.run('cd {} && npm install'.format(path), profile=True)
        self._cuisine.core.dir_remove('$appDir/S3', recursive=True)
        self._cuisine.core.run('mv {} $appDir/'.format(path))

        cmd = 'S3DATAPATH={data} S3METADATAPATH={meta} npm start'.format(
            data=storageLocation,
            meta=metaLocation,
        )

        content = self._cuisine.core.file_read('$appDir/S3/package.json')
        pkg = j.data.serializer.json.loads(content)
        pkg['scripts']['start_location'] = cmd

        content = j.data.serializer.json.dumps(pkg, indent=True)
        self._cuisine.core.file_write('$appDir/S3/package.json', content)

        if start:
            self.start()

    def start(self, name=NAME):
        path = j.sal.fs.joinPaths(j.dirs.appDir, 'S3')
        self._cuisine.core.run('cd {} && npm run start_location'.format(path), profile=True)

    def test(self):
        # put/get file over S3 interface using a python S3 lib
        raise NotImplementedError
