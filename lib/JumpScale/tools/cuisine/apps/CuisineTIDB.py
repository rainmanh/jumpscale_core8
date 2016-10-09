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

        self._cuisine.core.run('cd /tmp/tidb/ && curl {} | bash'.format(url), profile=True)

    def install(self, start=False):
        """
        download, install, move files to appropriate places, and create relavent configs
        """
        script = '''
        mv /tmp/tidb/bin/* $binDir/
        '''
        self._cuisine.core.execute_bash(script)

        if start:
            self.start()

    def build(self, start=True, install=True):
        """
        Build requires both golang and rust to be available on the system
        """
        self._build()
        if install:
            self.install(start)

    def start(self, clusterId=1):
        """
        Read docs here.
        https://github.com/pingcap/docs/blob/master/op-guide/clustering.md
        """

        # Start a standalone cluster

        # TODO: make it possible to start multinode cluster.
        config = {
            'clusterId': clusterId,
            'dataDir': j.sal.fs.joinPaths(j.dirs.varDir, 'tidb'),
        }

        self._cuisine.processmanager.ensure(
            'tipd',
            'pd-server --cluster-id {clusterId} \
            --data-dir={dataDir}'.format(**config),
        )

        self._cuisine.processmanager.ensure(
            'tikv',
            'tikv-server -I {clusterId} -S raftkv \
            --pd 127.0.0.1:2379 -s tikv1'.format(**config)
        )

        self._cuisine.processmanager.ensure(
            'tidb',
            'tidb-server --store=tikv \
            --path="127.0.0.1:2379?cluster={clusterId}"'.format(**config)
        )

    def test(self):
        raise NotImplementedError
        # do some basic test to show how it works
        # deploy 3 instances of tikv and then put behind tidb
        # use standard mysql python client to do a test
