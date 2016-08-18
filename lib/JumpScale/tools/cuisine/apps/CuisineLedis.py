from JumpScale import j
import os

from ActionDecorator import ActionDecorator


"""
please ensure that the start and build methods are separate and
the build doesnt place anyfile outside opt as it will be used in aysfs mounted system
"""


class actionrun(ActionDecorator):

    def __init__(self, *args, **kwargs):
        ActionDecorator.__init__(self, *args, **kwargs)
        self.selfobjCode = "cuisine=j.tools.cuisine.getFromId('$id');selfobj=cuisine.apps.ledis"

base = j.tools.cuisine.getBaseClass()


class Ledis(base):

    @actionrun(action=True)
    def build(self, backend="leveldb"):
        self.cuisine.installer.base()
        if self.cuisine.core.isUbuntu:

            C = """
            #!/bin/bash
            set -x

            cd {ledisdir}
            #set build and run environment
            source dev.sh

            make
            """
            self.cuisine.golang.install()
            self.cuisine.git.pullRepo("https://github.com/siddontang/ledisdb", dest="$goDir/src/github.com/siddontang/ledisdb")


            #set the backend in the server config
            ledisdir = self.cuisine.core.args_replace("$goDir/src/github.com/siddontang/ledisdb")

            configcontent = self.cuisine.core.file_read(os.path.join(ledisdir, "config", "config.toml"))
            ledisdir = self.cuisine.core.args_replace("$goDir/src/github.com/siddontang/ledisdb")

            if backend == "rocksdb":
                self._preparerocksdb()
            elif backend == "leveldb":
                rc, out, err = self._prepareleveldb()
            else:
                raise NotImplementedError
            configcontent.replace('db_name = "leveldb"', 'db_name = "%s"'%backend)

            self.cuisine.core.file_write("/tmp/ledisconfig.toml", configcontent)

            script = C.format(ledisdir=ledisdir)
            out = self.cuisine.core.run_script(script, profile=True)

    def _prepareleveldb(self):
        #execute the build script in tools/build_leveldb.sh
        # it will install snappy/leveldb in /usr/local{snappy/leveldb} directories
        ledisdir = self.cuisine.core.args_replace("$goDir/src/github.com/siddontang/ledisdb")
        #leveldb_build file : ledisdir/tools/build_leveldb.sh
        rc, out, err = self.cuisine.core.run("bash {ledisdir}/tools/build_leveldb.sh".format(ledisdir=ledisdir))
        return rc, out, err

    def _preparerocksdb(self):
        raise NotImplementedError

    @actionrun(force=True)
    def install(self, start=True):
        ledisdir = self.cuisine.core.args_replace("$goDir/src/github.com/siddontang/ledisdb")

        #rc, out, err = self.cuisine.core.run("cd {ledisdir} && source dev.sh && make install".format(ledisdir=ledisdir), profile=True)
        self.cuisine.core.file_copy("/tmp/ledisconfig.toml", dest="$tmplsDir/cfg/ledisconfig.toml")
        self.cuisine.core.file_copy("{ledisdir}/bin/*".format(ledisdir=ledisdir), dest="$binDir")
        self.cuisine.core.file_copy("{ledisdir}/dev.sh".format(ledisdir=ledisdir), dest="$tmplsDir/ledisdev.sh")

        if start:
            self.start()

    def start(self):
        cmd = "source $tmplsDir/ledisdev.sh && $binDir/ledis-server -config $tmplsDir/cfg/ledisconfig.toml"
        self.cuisine.processmanager.ensure(name='ledis', cmd=cmd)
