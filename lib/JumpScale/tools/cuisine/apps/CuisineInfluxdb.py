from JumpScale import j


from ActionDecorator import ActionDecorator


"""
please ensure that the start and build methods are separate and
the build doesnt place anyfile outside opt as it will be used in aysfs mounted system
"""


class actionrun(ActionDecorator):

    def __init__(self, *args, **kwargs):
        ActionDecorator.__init__(self, *args, **kwargs)
        self.selfobjCode = "cuisine=j.tools.cuisine.getFromId('$id');selfobj=cuisine.apps.influxdb"

base=j.tools.cuisine.getBaseClass()
class Influxdb(base):

    @actionrun(action=True)
    def install(self,dependencies=True, start=False):

        if dependencies:
            self.cuisine.installer.base()
            self.cuisine.package.mdupdate()

        if self.cuisine.core.isMac:
            self.cuisine.package.install('influxdb')
            self.cuisine.core.dir_ensure("$tmplsDir/cfg/influxdb")
            self.cuisine.core.file_copy("/usr/local/etc/influxdb.conf", "$tmplsDir/cfg/influxdb/influxdb.conf")

        elif self.cuisine.core.isUbuntu:
            self.cuisine.core.dir_ensure("$tmplsDir/cfg/influxdb",force=False)
            C= """
            set -ex
            cd $tmpDir
            wget https://dl.influxdata.com/influxdb/releases/influxdb-0.13.0_linux_amd64.tar.gz
            tar xvfz influxdb-0.13.0_linux_amd64.tar.gz
            cp influxdb-0.13.0-1/usr/bin/influxd $binDir
            cp influxdb-0.13.0-1/etc/influxdb/influxdb.conf $tmplsDir/cfg/influxdb/influxdb.conf"""
            self.cuisine.core.run_script(C, profile=True, action=True)
            self.cuisine.bash.addPath(self.cuisine.core.args_replace("$binDir"))
        else:
            raise RuntimeError("cannot install, unsuported platform")

        binPath = self.cuisine.bash.cmdGetPath('influxd')
        self.cuisine.core.dir_ensure("$varDir/data/influxdb")
        self.cuisine.core.dir_ensure("$varDir/data/influxdb/meta")
        self.cuisine.core.dir_ensure("$varDir/data/influxdb/data")
        self.cuisine.core.dir_ensure("$varDir/data/influxdb/wal")
        content = self.cuisine.core.file_read('$tmplsDir/cfg/influxdb/influxdb.conf')
        cfg = j.data.serializer.toml.loads(content)
        cfg['meta']['dir'] = "$varDir/data/influxdb/meta"
        cfg['data']['dir'] = "$varDir/data/influxdb/data"
        cfg['data']['wal-dir'] = "$varDir/data/influxdb/data"
        self.cuisine.core.dir_ensure('$cfgDir/influxdb')
        self.cuisine.core.file_write('$cfgDir/influxdb/influxdb.conf', j.data.serializer.toml.dumps(cfg))
        cmd = "%s -config $cfgDir/influxdb/influxdb.conf" % (binPath)
        cmd = self.cuisine.core.args_replace(cmd)
        self.cuisine.core.file_write("/opt/jumpscale8/bin/start_influxdb.sh",cmd,777,replaceArgs=True)

        if start:
            self.start()

    @actionrun()
    def build(self, start=True):
        raise RuntimeError("not implemented")

    @actionrun(force=True)
    def start(self):
        binPath = self.cuisine.bash.cmdGetPath('influxd')
        cmd = "%s -config $cfgDir/influxdb/influxdb.conf" % (binPath)
        self.cuisine.process.kill("influxdb")
        self.cuisine.processmanager.ensure("influxdb", cmd=cmd, env={}, path="")
