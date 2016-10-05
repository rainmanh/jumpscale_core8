from JumpScale import j
from time import sleep


app = j.tools.cuisine._getBaseAppClass()


class CuisineTIDB(app):
    NAME = 'tidb'

    def __init__(self, executor, cuisine):
        self._executor = executor
        self._cuisine = cuisine

    def _build(self):
        # TODO: *1
        # SEE: https://github.com/pingcap/tidb
        # deploy on top of tikv (which is distributed database backend on top of paxos)
        # WILL BE BACKEND FOR e.g. OWNCLOUD / GOGS
        url = 'https://raw.githubusercontent.com/pingcap/docs/master/scripts/build.sh'
        self._cuisine.core.dir_ensure('/tmp/tidb')

        self._cuisine.core.run('cd /tmp/tidb/ && curl {} | bash'.format(url))

    def install(self, start=True):
        """
        download, install, move files to appropriate places, and create relavent configs
        """

        # TODO: *1
        if start:
            self.start("???")

    def build(self, start=True, install=True):
        """
        Build requires both golang and rust to be available on the system
        """
        self._build()
        if install:
            self.install(start)

    def start(self, name="???"):
        # TODO:*1
        raise NotImplementedError

    def test(self):
        raise NotImplementedError
        # do some basic test to show how it works
        # deploy 3 instances of tikv and then put behind tidb
        # use standard mysql python client to do a test
