from JumpScale import j
from time import sleep
import MySQLdb

app = j.tools.cuisine._getBaseAppClass()


class TIDBContextManager:

    def __enter__(self):
        self._connection = MySQLdb.connect("127.0.0.1")
        return self

    def create_database(self, database):
        """
        Creates a database.
        """
        cursor = self._connection.cursor()
        SQL = """CREATE DATABASE {database};""".format(database=database)
        print("Executing SQL", SQL)
        cursor.execute(SQL)
        self._connection.commit()

    def drop_database(self, database):
        """
        Drops database if exists
        """
        cursor = self._connection.cursor()
        SQL = """DROP DATABASE IF EXISTS {database}  ;""".format(database=database)
        print("Executing SQL", SQL)
        cursor.execute(SQL)
        self._connection.commit()

    def create_dbuser(self, host, username, passwd):
        """
        Creates a user in database.
        """
        cursor = self._connection.cursor()
        SQL = """CREATE USER '{username}'@'{host}' IDENTIFIED BY '{passwd}' ;""".format(host=host, username=username, passwd=passwd)
        print("Executing SQL", SQL)
        cursor.execute(SQL)
        self._connection.commit()

    def grant_user(self, host, database, username):
        """
        Grants full access on certain databse.
        """
        SQL = """grant all on {database}.* to '{username}'@'{host}' ;""".format(database=database, host=host, username=username)
        cursor = self._connection.cursor()
        print("Executing SQL", SQL)
        cursor.execute(SQL)
        self._connection.commit()

    def __exit__(self, type, value, traceback):
        self._connection.close()


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
    NAME = 'tidb'

    def __init__(self, executor, cuisine):
        self._executor = executor
        self._cuisine = cuisine
        self.dbman = TIDBContextManager

    def _build(self):
        # TODO: *1
        # SEE: https://github.com/pingcap/tidb
        # deploy on top of tikv (which is distributed database backend on top of paxos)
        # WILL BE BACKEND FOR e.g. OWNCLOUD / GOGS
        url = 'https://raw.githubusercontent.com/pingcap/docs/master/scripts/build.sh'
        self._cuisine.core.dir_ensure('/tmp/tidb')

        self._cuisine.core.run('cd /tmp/tidb/ && curl {} | bash'.format(url), profile=True)

    # TODO:  Currently install with start=False and then run start_tipd, start_tikv, start_tidb separately
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

    def start_pd_server(self, clusterId=1):
        config = {
            'clusterId': clusterId,
            'dataDir': j.sal.fs.joinPaths(j.dirs.varDir, 'tidb'),
        }
        self._cuisine.processmanager.ensure(
            'tipd',
            'pd-server --cluster-id {clusterId} \
            --data-dir={dataDir}'.format(**config),
        )

    def start_tikv(self, clusterId=1):
        config = {
            'clusterId': clusterId,
            'dataDir': j.sal.fs.joinPaths(j.dirs.varDir, 'tidb'),
        }
        self._cuisine.processmanager.ensure(
            'tikv',
            'tikv-server -I {clusterId} -S raftkv \
            --pd 127.0.0.1:2379 -s tikv1'.format(**config)
        )

    def start_tidb(self, clusterId=1):
        config = {
            'clusterId': clusterId,
            'dataDir': j.sal.fs.joinPaths(j.dirs.varDir, 'tidb'),
        }
        self._cuisine.processmanager.ensure(
            'tidb',
            'tidb-server -P 3306 --store=tikv \
            --path="127.0.0.1:2379?cluster={clusterId}"'.format(**config)
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
        cmd = "netstat | grep tidb-server"
        rc, out, err = self._cuisine.core.run(cmd)
        tries = 0  # Give it sometime to start.
        while rc != 0 and tries < 3:
            sleep(2)
            tries += 1
        # tries = 0  # Give it sometime to start.
        # while "tikv" not in self._cuisine.processmanager.list( and tries < 3:
        #     sleep(2)
        #     tries += 1
        self.start_tidb()

    def start(self, clusterId=1):
        return self.simple_start()

    def test(self):
        raise NotImplementedError
        # do some basic test to show how it works
        # deploy 3 instances of tikv and then put behind tidb
        # use standard mysql python client to do a test
