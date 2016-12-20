from JumpScale import j
from time import sleep


app = j.tools.cuisine._getBaseAppClass()


class CuisineS3Server(app):
    NAME = 's3server'

    def install(self, start=False, storageLocation="/data/", metaLocation="/meta/"):
        """
        put backing store on /storage/...
        """
        path = self.cuisine.development.git.pullRepo('https://github.com/scality/S3.git')
        self.cuisine.core.run('cd {} && npm install'.format(path), profile=True)
        self.cuisine.core.dir_remove('$JSAPPSDIR/S3', recursive=True)
        self.cuisine.core.run('mv {} $JSAPPSDIR/'.format(path))

        cmd = 'S3DATAPATH={data} S3METADATAPATH={meta} npm start'.format(
            data=storageLocation,
            meta=metaLocation,
        )

        content = self.cuisine.core.file_read('$JSAPPSDIR/S3/package.json')
        pkg = j.data.serializer.json.loads(content)
        pkg['scripts']['start_location'] = cmd

        content = j.data.serializer.json.dumps(pkg, indent=True)
        self.cuisine.core.file_write('$JSAPPSDIR/S3/package.json', content)

        if start:
            self.start()

    def start(self, name=NAME):
        path = j.sal.fs.joinPaths(j.dirs.JSAPPSDIR, 'S3')
        self.cuisine.core.run('cd {} && npm run start_location'.format(path), profile=True)

    def test(self):
        # put/get file over S3 interface using a python S3 lib
        raise NotImplementedError
