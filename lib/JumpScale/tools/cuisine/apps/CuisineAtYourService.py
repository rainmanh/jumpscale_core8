from JumpScale import j
from time import sleep


base = j.tools.cuisine._getBaseClass()


class CuisineAtYourService(base):


    def install(self):
        self.cuisine.development.pip.multiInstall([
            'sanic==0.3.0',
            'jsonschema'
        ])

        base_dir = j.sal.fs.joinPaths('$JSAPPSDIR','atyourservice')

        self.cuisine.core.dir_ensure(base_dir)

        # link apidocs and index.html
        self.cuisine.core.file_link(
            j.sal.fs.joinPaths('$CODEDIR', 'github/jumpscale/jumpscale_core8/apps/atyourservice/server/apidocs'),
            j.sal.fs.joinPaths(base_dir,'apidocs')
        )

        self.cuisine.core.file_link(
            j.sal.fs.joinPaths('$CODEDIR', 'github/jumpscale/jumpscale_core8/apps/atyourservice/server/index.html'),
            j.sal.fs.joinPaths(base_dir,'index.html')
        )

        self.cuisine.core.file_link(
            j.sal.fs.joinPaths('$CODEDIR', 'github/jumpscale/jumpscale_core8/apps/atyourservice/main.py'),
            j.sal.fs.joinPaths(base_dir,'main.py')
        )

    def start(self, host='localhost', port=5000):
        cmd = 'jspython $JSAPPSDIR/atyourservice/main.py -h {host} -p {port}'.format(host=host, port=port)
        self.cuisine.processmanager.ensure(name='atyourservice', cmd=cmd)

    def stop(self):
        self.cuisine.processmanager.stop(name='atyourservice')
