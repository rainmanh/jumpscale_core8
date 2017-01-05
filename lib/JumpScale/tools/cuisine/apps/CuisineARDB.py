from JumpScale import j


app = j.tools.cuisine._getBaseAppClass()


class CuisineARDB(app):
    NAME = 'ardb'

    def _init(self):
        self.BUILDDIRFDB = self.replace("$BUILDDIR/forestdb/")
        self.CODEDIRFDB = self.replace("$CODEDIR/github/couchbase/forestdb")
        self.CODEDIRARDB = self.replace("$CODEDIR/github/yinqiwen/ardb")
        self.BUILDDIRARDB = self.replace("$BUILDDIR/ardb/")

    def build(self, destpath="", reset=False):
        """
        @param destpath, if '' then will be $TMPDIR/build/openssl
        """
        if self.doneGet("build") and not reset:
            return
        if reset:
            self.cuisine.core.run("rm -rf %s" % self.BUILDDIR)

        # not needed to build separately is done in ardb automatically
        # self.buildForestDB(reset=reset)

        self.buildARDB(reset=reset)

    def buildForestDB(self, reset=False):
        if self.doneGet("buildforestdb") and not reset:
            return

        self.cuisine.package.install("cmake")
        self.cuisine.package.install("libsnappy-dev")

        url = "git@github.com:couchbase/forestdb.git"
        cpath = self.cuisine.development.git.pullRepo(url, tag="v1.2", reset=reset)

        assert cpath.rstrip("/") == self.CODEDIRFDB.rstrip("/")

        C = """
            set -ex
            cd $CODEDIRFDB
            mkdir build
            cd build
            cmake ../
            make all
            rm -rf $BUILDDIRFDB/
            mkdir -p $BUILDDIRFDB
            cp forestdb_dump* $BUILDDIRFDB/
            cp forestdb_hexamine* $BUILDDIRFDB/
            cp libforestdb* $BUILDDIRFDB/
            """
        self.cuisine.core.run(self.replace(C))
        self.doneSet("buildforestdb")

    def buildARDB(self, reset=False, storageEngine="forestdb"):
        """
        @param storageEngine rocksdb or forestdb
        """
        if self.doneGet("buildardb") and not reset:
            return

        if self.cuisine.platformtype.isOSX():
            storageEngine = "rocksdb"
            # self.cuisine.package.install("boost")

        self.cuisine.package.install("wget")

        url = "git@github.com:yinqiwen/ardb.git"
        cpath = self.cuisine.development.git.pullRepo(url, tag="v0.9.3", reset=reset)
        print(cpath)

        assert cpath.rstrip("/") == self.CODEDIRARDB.rstrip("/")

        C = """
            set -ex
            cd $CODEDIRARDB
            # cp $BUILDDIRFDB/libforestdb* .
            storage_engine=$storageEngine make
            rm -rf $BUILDDIRARDB/
            mkdir -p $BUILDDIRARDB
            cp src/ardb-server $BUILDDIRARDB/
            cp ardb.conf $BUILDDIRARDB/
            """
        C = C.replace("$storageEngine", storageEngine)
        self.cuisine.core.run(self.replace(C))

        self.doneSet("buildardb")

    def install(self, reset=False, start=True):
        """
        as backend use ForestDB
        """
        if self.doneGet("install") and not reset:
            return
        self.buildARDB()

        self.core.file_copy("$BUILDDIR/ardb/ardb-server", "$BINDIR/ardb-server")
        self.core.file_copy("$BUILDDIR/ardb/ardb.conf", "$CFGDIR/ardb.conf")

        config = self.core.file_read("$CFGDIR/ardb.conf")
        datadir = self.replace("$VARDIR/data/ardb")
        config = config.replace("${ARDB_HOME}", datadir)
        config = config.replace("0.0.0.0:16379", "localhost:16379")

        self.core.dir_ensure(datadir)

        self.core.file_write("$CFGDIR/ardb.conf", config)

        self.doneSet("install")

        if start:
            self.start()

    def start(self, reset=False):
        if not reset and self.doneGet("start"):
            return
        if reset:
            self.stop()
        cmd = "$BINDIR/ardb-server $CFGDIR/ardb.conf"
        self.cuisine.process.kill("ardb-server")
        self.cuisine.processmanager.ensure(name="ardb-server", cmd=cmd, env={}, path="")
        self.test()
        self.doneSet("start")

    def stop(self):
        self.cuisine.processmanager.stop("ardb-server")

    def getClient(self):
        pass

    def test(self):
        """
        do some test through normal redis client
        """
        r = j.clients.redis.get(port=16379)
        r.set("test", "test")
        assert r.get("test") == b"test"
        r.delete("test")
