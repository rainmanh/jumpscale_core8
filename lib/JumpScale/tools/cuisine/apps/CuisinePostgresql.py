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
        cd $tmpDir
        cd postgresql-9.6.1
        ./configure
        make

        """
        self._cuisine.core.execute_bash(cmd, profile=True)

    def install(self, reset=False, start=False):
        if reset is False and self.isInstalled():
            return
        if start:
            self.start()
