from JumpScale import j

app = j.tools.cuisine._getBaseAppClass()


class CuisineGrafana(app):

    NAME = 'grafana-server'

    def build(self, reset=False):

        if reset is False and self.isInstalled():
            return

        if self._cuisine.core.isUbuntu:
            C = """
            cd $tmpDir
            wget https://grafanarel.s3.amazonaws.com/builds/grafana_3.1.1-1470047149_amd64.deb
            sudo apt-get install -y adduser libfontconfig
            sudo dpkg -i grafana_3.1.1-1470047149_amd64.deb

            """
            self._cuisine.core.execute_bash(C, profile=True)
        else:
            raise RuntimeError("platform not supported")

    def install(self, start=False, influx_addr='127.0.0.1', influx_port=8086, port=3000):

        self._cuisine.core.file_copy("/usr/sbin/grafana*", dest="$binDir")

        self._cuisine.core.dir_ensure("$appDir/grafana")
        self._cuisine.core.file_copy("/usr/share/grafana/", "$appDir/", recursive=True)

        if self._cuisine.core.file_exists("/usr/share/grafana/conf/defaults.ini"):
            cfg = self._cuisine.core.file_read("/usr/share/grafana/conf/defaults.ini")
        else:
            cfg = self._cuisine.core.file_read('$tmpDir/cfg/grafana/conf/defaults.ini')
        self._cuisine.core.file_write('$cfgDir/grafana/grafana.ini', cfg)

        if start:
            self.start(influx_addr, influx_port, port)

    def start(self, influx_addr='127.0.0.1', influx_port=8086, port=3000):

        cmd = "$binDir/grafana-server --config=$cfgDir/grafana/grafana.ini\n"
        cmd = self._cuisine.core.args_replace(cmd)
        self._cuisine.core.file_write("/opt/jumpscale8/bin/start_grafana.sh", cmd, 777, replaceArgs=True)
        self._cuisine.process.kill("grafana-server")
        self._cuisine.processmanager.ensure("grafana-server", cmd=cmd, env={}, path='$appDir/grafana')
        grafanaclient = j.clients.grafana.get(
            url='http://%s:%d' % (self._cuisine.core._executor.addr, port), username='admin', password='admin')
        data = {
            'type': 'influxdb',
            'access': 'proxy',
            'database': 'statistics',
            'name': 'influxdb_main',
            'url': 'http://%s:%u' % (influx_addr, influx_port),
            'user': 'admin',
            'password': 'passwd',
            'default': True,
        }
        import time
        import requests
        now = time.time()
        while time.time() - now < 10:
            try:
                grafanaclient.addDataSource(data)
                if not grafanaclient.listDataSources():
                    continue
                break
            except requests.exceptions.ConnectionError:
                time.sleep(1)
                pass
