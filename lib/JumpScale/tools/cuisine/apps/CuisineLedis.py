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
    def build(self, backend="leveldb", start=True):
        #self.cuisine.installer.base()
        if self.cuisine.core.isUbuntu:

            C = """
            #!/bin/bash
            set -x

            cd {ledisdir}
            #set build and run environment
            source dev.sh

            make
            make install
            """
            #self.cuisine.golang.install()
            self.cuisine.git.pullRepo("https://github.com/siddontang/ledisdb", dest="$goDir/src/github.com/siddontang/ledisdb")
            #self.cuisine.golang.godep("github.com/siddontang/ledisdb", action=True)
            ledisdir = self.cuisine.core.args_replace("$goDir/src/github.com/siddontang/ledisdb")

            #set the backend in the server config

            configcontent = self.cuisine.core.file_read(os.path.join(ledisdir, "config", "config.toml"))
            #import pudb; pu.db

            if backend == "rocksdb":
                self._preparerocksdb()
            elif backend == "leveldb":
                rc, out, err = self._prepareleveldb()

            configcontent.replace('db_name = "leveldb"', 'db_name = "%s"'%backend)

            self.cuisine.core.file_write("$tmplsDir/cfg/ledisconfig.toml", configcontent)

            script = C.format(ledisdir=ledisdir)
            #import pudb; pu.db
            out = self.cuisine.core.run_script(script, profile=True)
            self.cuisine.core.file_copy("{ledisdir}/bin/*".format(ledisdir=ledisdir), dest="$binDir")
            self.cuisine.core.file_copy("{ledisdir}/dev.sh".format(ledisdir=ledisdir), dest="$tmplsDir/ledisdev.sh")

        if start:
            self.start()

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
    def start(self):
        cmd = "source $tmplsDir/ledisdev.sh && $binDir/ledis-server -config $tmplsDir/cfg/ledisconfig.toml"
        self.cuisine.processmanager.ensure(name='ledis', cmd=cmd)
