from JumpScale import j
import os

app = j.tools.cuisine._getBaseAppClass()

class CuisineLedis(app):
    NAME = "ledis-server"
    def build(self, backend="leveldb", reset=False):
        if reset == False and self.isInstalled():
            return

        if self._cuisine.core.isUbuntu:

            C = """
            #!/bin/bash
            set -x

            cd {ledisdir}
            #set build and run environment
            source dev.sh

            make
            """
            self._cuisine.golang.install()
            self._cuisine.git.pullRepo("https://github.com/siddontang/ledisdb",
                                       dest="$goDir/src/github.com/siddontang/ledisdb")

            # set the backend in the server config
            ledisdir = self._cuisine.core.args_replace("$goDir/src/github.com/siddontang/ledisdb")

            configcontent = self._cuisine.core.file_read(os.path.join(ledisdir, "config", "config.toml"))
            ledisdir = self._cuisine.core.args_replace("$goDir/src/github.com/siddontang/ledisdb")

            if backend == "rocksdb":
                self._preparerocksdb()
            elif backend == "leveldb":
                rc, out, err = self._prepareleveldb()
            else:
                raise NotImplementedError
            configcontent.replace('db_name = "leveldb"', 'db_name = "%s"' % backend)

            self._cuisine.core.file_write("/tmp/ledisconfig.toml", configcontent)

            script = C.format(ledisdir=ledisdir)
            out = self._cuisine.core.run_script(script, profile=True)

    def _prepareleveldb(self):
        # execute the build script in tools/build_leveldb.sh
        # it will install snappy/leveldb in /usr/local{snappy/leveldb} directories
        ledisdir = self._cuisine.core.args_replace("$goDir/src/github.com/siddontang/ledisdb")
        # leveldb_build file : ledisdir/tools/build_leveldb.sh
        rc, out, err = self._cuisine.core.run("bash {ledisdir}/tools/build_leveldb.sh".format(ledisdir=ledisdir))
        return rc, out, err

    def _preparerocksdb(self):
        raise NotImplementedError

    def install(self, start=True):
        ledisdir = self._cuisine.core.args_replace("$goDir/src/github.com/siddontang/ledisdb")

        #rc, out, err = self._cuisine.core.run("cd {ledisdir} && source dev.sh && make install".format(ledisdir=ledisdir), profile=True)
        self._cuisine.core.file_copy("/tmp/ledisconfig.toml", dest="$tmplsDir/cfg/ledisconfig.toml")
        self._cuisine.core.file_copy("{ledisdir}/bin/*".format(ledisdir=ledisdir), dest="$binDir")
        self._cuisine.core.file_copy("{ledisdir}/dev.sh".format(ledisdir=ledisdir), dest="$tmplsDir/ledisdev.sh")

        if start:
            self.start()

    def start(self):
        cmd = "source $tmplsDir/ledisdev.sh && $binDir/ledis-server -config $tmplsDir/cfg/ledisconfig.toml"
        self._cuisine.processmanager.ensure(name='ledis', cmd=cmd)
