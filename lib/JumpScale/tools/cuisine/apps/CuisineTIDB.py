from JumpScale import j
from time import sleep


app = j.tools.cuisine._getBaseAppClass()

class CuisineTIDB(app):
    """
    Installs TIDB.

    # TODO :*1 FIX install method (to chain 3 start as a simple start method)
    build(start=False)
    then start manually
    start_tipd()
    start_tikv()
    start_tidb()


    """
    NAME = 'tidb-server'

    def __init__(self, executor, cuisine):
        self._executor = executor
        self._cuisine = cuisine


    def _build(self):
        # TODO: *1
        # SEE: https://github.com/pingcap/tidb
        # deploy on top of tikv (which is distributed database backend on top of paxos)
        # WILL BE BACKEND FOR e.g. OWNCLOUD / GOGS
        self._cuisine.package.mdupdate()
        self._cuisine.package.install('build-essential')

        self._cuisine.core.dir_ensure("/optvar/build")
        tidb_url = 'http://download.pingcap.org/tidb-latest-linux-amd64.tar.gz'
        dest = j.sal.fs.joinPaths("/optvar/build", 'tidb-latest-linux-amd64.tar.gz')
        # build_script = self.cuisine.core.file_download('https://raw.githubusercontent.com/pingcap/docs/master/scripts/build.sh', \
        #     j.sal.fs.joinPaths(self.BUILDDIR, 'build.sh'),minsizekb=0)
        #
        # self.cuisine.core.run('cd {builddir}; bash {build}'.format(builddir=self.BUILDDIR, build=build_script), profile=True, timeout=1000)
        self._cuisine.core.file_download(tidb_url, dest)
        self._cuisine.core.run('cd /optvar/build && tar xvf /optvar/build/tidb-latest-linux-amd64.tar.gz && mv /optvar/build/tidb-latest-linux-amd64 /optvar/build/tidb  ')

    # TODO:  Currently install with start=False and then run start_tipd, start_tikv, start_tidb separately
    def install(self, start=False):
        """
        download, install, move files to appropriate places, and create relavent configs

        """
        script = '''
        mv /optvar/build/tidb/bin/* $binDir/
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

    def start_pd_server(self, clusterId=1):
        config = {
            'clusterId': clusterId,
            'dataDir': j.sal.fs.joinPaths(j.dirs.varDir, 'tidb_data'),
        }
        self._cuisine.core.dir_ensure(config['dataDir'])
        cmd = 'pd-server --data-dir={dataDir}'.format(**config)
        # print("CMD PD-SERVER: ", cmd)
        self._cuisine.processmanager.ensure(
            'tipd',
            cmd,
        )

    def start_tikv(self, clusterId=1):
        config = {
            'clusterId': clusterId,
            'dataDir': j.sal.fs.joinPaths(j.dirs.varDir, 'tidb_data'),

        }
        cmd = 'tikv-server --pd="127.0.0.1:2379" --store=tikv'.format(**config)
        # print("CMD: TIKV: ", cmd)

        self._cuisine.processmanager.ensure(
            'tikv',
            cmd
        )

    def start_tidb(self, clusterId=1):
        config = {
            'clusterId': clusterId,
            'dataDir': j.sal.fs.joinPaths(j.dirs.varDir, 'tidb_data'),
        }
        cmd = 'tidb-server -P 3306 --store=tikv --path="127.0.0.1:2379"'.format(**config)
        # print("CMD: TIDB: ", cmd)
        self._cuisine.processmanager.ensure(
            'tidb',
            cmd
        )

    def simple_start(self, clusterId=1):
        """
        Read docs here.
        https://github.com/pingcap/docs/blob/master/op-guide/clustering.md
        """
        # Start a standalone cluster
        # TODO: make it possible to start multinode cluster.
        self.start_pd_server()
        self.start_tikv()
        cmd = "ps aux | grep tikv-server"
        rc, out, err = self._cuisine.core.run(cmd, die=False)
        tries = 0  # Give it sometime to start.
        while rc != 0 and tries < 3:
            rc, out, err = self._cuisine.core.run(cmd, die=False)
            sleep(2)
            tries += 1
        self.start_tidb()
        # tries = 0  # Give it sometime to start.
        # while "tikv" not in self._cuisine.processmanager.list( and tries < 3:
        #     sleep(2)
        #     tries += 1


    def stop(self):
        self._cuisine.processmanager.stop("tidp")
        self._cuisine.processmanager.stop("tikv")
        self._cuisine.processmanager.stop("tidb")

    def start(self, clusterId=1):
        return self.simple_start()

    def test(self):
        raise NotImplementedError
        # do some basic test to show how it works
        # deploy 3 instances of tikv and then put behind tidb
        # use standard mysql python client to do a test
