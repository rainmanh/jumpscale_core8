from JumpScale import j

app = j.tools.cuisine._getBaseAppClass()


class CuisinePostgresql(app):
    NAME = "Postgresql"

    def __init__(self, executor, cuisine):
        self._executor = executor
        self._cuisine = cuisine

    def build(self):
        postgre_url = 'https://ftp.postgresql.org/pub/source/v9.6.1/postgresql-9.6.1.tar.gz'
        dest = '$tmpDir/postgresql-9.6.1.tar.gz'
        self._cuisine.core.file_download(postgre_url, dest)
        self._cuisine.core.run('cd $tmpDir; tar xvf $tmpDir/postgresql-9.6.1.tar.gz')
        cmd = """
        cd $tmpDir/postgresql-9.6.1
        ./configure
        make

        """
        self._cuisine.core.execute_bash(cmd, profile=True)

    def _group_exists(self,groupname):
        return groupname in open("/etc/group").read()

    def install(self, reset=False, start=False, port=5432):
        if reset is False and self.isInstalled():
            return
        cmd = """
        cd $tmpDir/postgresql-9.6.1
        make install prefix=$appDir/pgsql bindir=$binDir/postgres sysconfdir=$cfgDir libdir=$libDir/postgres with-pgport=%s
        """ % str(port)

        self._cuisine.core.dir_ensure("$appDir/pgsql")
        self._cuisine.core.dir_ensure("$binDir/postgres")
        self._cuisine.core.dir_ensure("$libDir/postgres")
        self._cuisine.core.execute_bash(cmd, profile=True)
        if not self._group_exists("postgres"):
            self._cuisine.core.run('adduser --system --quiet --home $libDir/postgres --no-create-home \
        --shell /bin/bash --group --gecos "PostgreSQL administrator" postgres')
        c = """
        cd $appDir/pgsql
        mkdir data
        mkdir log
        chown postgres $binDir/postgres
        chown postgres $appDir/pgsql/
        sudo -u posrgres $binDir/postgres/initdb -D $appDir/pgsql/data
        """
        self._cuisine.core.execute_bash(c, profile=True)
        if start:
            self.start()

    def start(self):
        cmd = """
        sudo -u postgres $binDir/postgres/pg_ctl -D $appDir/pgsql/data -l $appDir/pgsql/log/logfile start
        """
        self._cuisine.core.execute_bash(cmd, profile=True)
