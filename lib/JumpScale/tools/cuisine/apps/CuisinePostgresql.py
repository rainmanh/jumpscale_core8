from JumpScale import j

app = j.tools.cuisine._getBaseAppClass()


class CuisinePostgresql(app):
    NAME = "postgres"

    def build(self):
        postgre_url = 'https://ftp.postgresql.org/pub/source/v9.6.1/postgresql-9.6.1.tar.gz'
        dest = '$tmpDir/postgresql-9.6.1.tar.gz'
        self.cuisine.core.file_download(postgre_url, dest)
        self.cuisine.core.run('cd $tmpDir; tar xvf $tmpDir/postgresql-9.6.1.tar.gz')
        self.cuisine.core.dir_ensure("$appDir/pgsql")
        self.cuisine.core.dir_ensure("$binDir")
        self.cuisine.core.dir_ensure("$libDir/postgres")
        cmd = """
        apt-get --assume-yes install libreadline-dev
        cd $tmpDir/postgresql-9.6.1
        ./configure --prefix=$appDir/pgsql --bindir=$binDir --sysconfdir=$cfgDir --libdir=$libDir/postgres --datarootdir=$appDir/pgsql/share
        make
        """
        self.cuisine.core.execute_bash(cmd, profile=True)
        # self.cuisine.core.run(' cp $tmpDir/pgsql /optvar/build/tidb

    def _group_exists(self, groupname):
        return groupname in open("/etc/group").read()

    def install(self, reset=False, start=False, port=5432):
        if reset is False and self.isInstalled():
            return
        cmd = """
        cd $tmpDir/postgresql-9.6.1
        make install with-pgport=%s
        """ % str(port)

        self.cuisine.core.execute_bash(cmd, profile=True)
        if not self._group_exists("postgres"):
            self.cuisine.core.run('adduser --system --quiet --home $libDir/postgres --no-create-home \
        --shell /bin/bash --group --gecos "PostgreSQL administrator" postgres')
        c = """
        cd $appDir/pgsql
        mkdir data
        mkdir log
        chown  -R postgres $appDir/pgsql/
        sudo -u postgres $binDir/initdb -D $appDir/pgsql/data --no-locale
        """
        self.cuisine.core.execute_bash(c, profile=True)
        if start:
            self.start()

    def start(self):
        cmd = """
        chown postgres $appDir/pgsql/log/
        sudo -u postgres $binDir/pg_ctl -D $appDir/pgsql/data -l $appDir/pgsql/log/logfile start
        """
        self.cuisine.core.execute_bash(cmd, profile=True)

    def stop(self):
        cmd = """
        sudo -u postgres $binDir/pg_ctl -D $appDir/pgsql/data -l $appDir/pgsql/log/logfile stop
        """
        self.cuisine.core.execute_bash(cmd, profile=True)
