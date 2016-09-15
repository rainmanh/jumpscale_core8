from JumpScale import j


app = j.tools.cuisine._getBaseAppClass()


class CuisineInfluxdb(app):
    NAME = "influxd"

    def install(self, dependencies=False, start=False, reset=False):
        if reset == False and self.isInstalled():
            return

        if dependencies:
            self._cuisine.package.mdupdate()

        if self._cuisine.core.isMac:
            self._cuisine.package.install('influxdb')
            self._cuisine.core.dir_ensure("$tmplsDir/cfg/influxdb")
            self._cuisine.core.file_copy("/usr/local/etc/influxdb.conf", "$tmplsDir/cfg/influxdb/influxdb.conf")

        elif self._cuisine.core.isUbuntu:
            self._cuisine.core.dir_ensure("$tmplsDir/cfg/influxdb")
            C = """
            set -ex
            cd $tmpDir
            wget https://dl.influxdata.com/influxdb/releases/influxdb-0.13.0_linux_amd64.tar.gz
            tar xvfz influxdb-0.13.0_linux_amd64.tar.gz
            cp influxdb-0.13.0-1/usr/bin/influxd $binDir
            cp influxdb-0.13.0-1/etc/influxdb/influxdb.conf $tmplsDir/cfg/influxdb/influxdb.conf"""
            self._cuisine.core.execute_bash(C, profile=True)
            self._cuisine.bash.addPath(self._cuisine.core.args_replace("$binDir"))
        else:
            raise RuntimeError("cannot install, unsuported platform")

        binPath = self._cuisine.bash.cmdGetPath('influxd')
        self._cuisine.core.dir_ensure("$varDir/data/influxdb")
        self._cuisine.core.dir_ensure("$varDir/data/influxdb/meta")
        self._cuisine.core.dir_ensure("$varDir/data/influxdb/data")
        self._cuisine.core.dir_ensure("$varDir/data/influxdb/wal")
        content = self._cuisine.core.file_read('$tmplsDir/cfg/influxdb/influxdb.conf')
        cfg = j.data.serializer.toml.loads(content)
        cfg['meta']['dir'] = self._cuisine.core.args_replace("$varDir/data/influxdb/meta")
        cfg['data']['dir'] = self._cuisine.core.args_replace("$varDir/data/influxdb/data")
        cfg['data']['wal-dir'] = self._cuisine.core.args_replace("$varDir/data/influxdb/data")
        self._cuisine.core.dir_ensure('$cfgDir/influxdb')
        self._cuisine.core.file_write('$cfgDir/influxdb/influxdb.conf', j.data.serializer.toml.dumps(cfg))
        cmd = "%s -config $cfgDir/influxdb/influxdb.conf" % (binPath)
        cmd = self._cuisine.core.args_replace(cmd)
        self._cuisine.core.file_write("/opt/jumpscale8/bin/start_influxdb.sh", cmd, 777, replaceArgs=True)

        if start:
            self.start()

    def build(self, start=True):
        raise RuntimeError("not implemented")

    def start(self):
        binPath = self._cuisine.bash.cmdGetPath('influxd')
        cmd = "%s -config $cfgDir/influxdb/influxdb.conf" % (binPath)
        self._cuisine.process.kill("influxdb")
        self._cuisine.processmanager.ensure("influxdb", cmd=cmd, env={}, path="")
