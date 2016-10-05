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
        raise NotImplementedError

    def install(self, start=True):
        """
        download, install, move files to appropriate places, and create relavent configs

        """
        # TODO: *1
        if start:
            self.start("???")

    def build(self, start=True, install=True):
        self._build()
        if install:
            self.install(start)

    def start(self, name="???"):
        # TODO:*1

    def test(self):
        raise NotImplementedError
        # do some basic test to show how it works
        # deploy 3 instances of tikv and then put behind tidb
        # use standard mysql python client to do a test
