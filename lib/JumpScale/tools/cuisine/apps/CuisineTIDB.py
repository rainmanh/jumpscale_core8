from JumpScale import j
from time import sleep


app = j.tools.cuisine._getBaseAppClass()


class CuisineTIDB(app): #TODO: *2 test on ovh4 over cuisine, use doneGet/Set
    """
    Installs TIDB.

    # TODO :*1 FIX install method (to chain 3 start as a simple start method)
    build(start=False)
    then start manually
    start_tipd()
    start_tikv()
    start_tidb()
    """
    NAME = 'tidb'

    def _build(self):
        pass

    def install(self, start=True):
        """
        download, install, move files to appropriate places, and create relavent configs

        """
        script = '''
        mv /tmp/tidb/bin/* $BINDIR/
        '''
        self.cuisine.core.execute_bash(script)

        if start:
            self.start()

    def build(self, start=True, install=True):
        """
        Build requires both golang and rust to be available on the system
        """
        # SEE: https://github.com/pingcap/tidb
        # deploy on top of tikv (which is distributed database backend on top of paxos)
        # WILL BE BACKEND FOR e.g. OWNCLOUD / GOGS
        self.cuisine.package.mdupdate()
        self.cuisine.package.install('build-essential')
        url = 'https://raw.githubusercontent.com/pingcap/docs/master/scripts/build.sh'
        self.cuisine.core.dir_ensure('/tmp/tidb')

        self.cuisine.core.run('cd /tmp/tidb/ && curl {} | bash'.format(url), profile=True)
        if install:
            self.install(start)

    def start_pd_server(self, clusterId=1):
        config = {
            'clusterId': clusterId,
            'dataDir': j.sal.fs.joinPaths(j.dirs.VARDIR, 'tidb'),
        }
        self.cuisine.processmanager.ensure(
            'tipd',
            'pd-server --cluster-id {clusterId} \
            --data-dir={dataDir}'.format(**config),
        )

    def start_tikv(self, clusterId=1):
        config = {
            'clusterId': clusterId,
            'dataDir': j.sal.fs.joinPaths(j.dirs.VARDIR, 'tidb'),
        }
        self.cuisine.processmanager.ensure(
            'tikv',
            'tikv-server -I {clusterId} -S raftkv \
            --pd 127.0.0.1:2379 -s tikv1'.format(**config)
        )

    def start_tidb(self, clusterId=1):
        config = {
            'clusterId': clusterId,
            'dataDir': j.sal.fs.joinPaths(j.dirs.VARDIR, 'tidb'),
        }
        self.cuisine.processmanager.ensure(
            'tidb',
            'tidb-server -P 3306 --store=tikv \
            --path="127.0.0.1:2379?cluster={clusterId}"'.format(**config)
        )

    def start(self, clusterId=1):
        """
        Read docs here.
        https://github.com/pingcap/docs/blob/master/op-guide/clustering.md
        """
        # Start a standalone cluster
        # TODO: make it possible to start multinode cluster.
        self.start_pd_server()
        self.start_tikv()
        cmd = "ps aux | grep tikv-server"
        rc, out, err = self.cuisine.core.run(cmd, die=False)
        tries = 0  # Give it sometime to start.
        while rc != 0 and tries < 3:
            rc, out, err = self.cuisine.core.run(cmd, die=False)
            sleep(2)
            tries += 1
        self.start_tidb()
        # tries = 0  # Give it sometime to start.
        # while "tikv" not in self.cuisine.processmanager.list( and tries < 3:
        #     sleep(2)
        #     tries += 1
