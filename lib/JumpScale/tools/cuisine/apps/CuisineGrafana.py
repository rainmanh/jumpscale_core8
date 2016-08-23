from JumpScale import j

app = j.tools.cuisine._getBaseAppClass()


class CuisineGrafana(app):

    NAME = 'grafana-server'

    def install(self, start=True, influx_addr='127.0.0.1', influx_port=8086, port=3000):
        #if self.isInstalled():
        #    return

        # TODO: *1 influx_addr & port not implemented to change in config file
        # TODO: *2 need to test the isLinux one,

        if self._cuisine.core.isUbuntu:
            C = """
            cd $tmpDir
            wget https://grafanarel.s3.amazonaws.com/builds/grafana_3.1.1-1470047149_amd64.deb
            sudo apt-get install -y adduser libfontconfig
            sudo dpkg -i grafana_3.1.1-1470047149_amd64.deb

            """
            # self._cuisine.core.pprint(C)
<<<<<<< Updated upstream
            self._cuisine.core.execute_bash(C, profile=True)
=======
            #self._cuisine.core.run_script(C, profile=True)
>>>>>>> Stashed changes
            self._cuisine.core.file_copy("/usr/sbin/grafana*", dest="$binDir")

            self._cuisine.core.dir_ensure("$appDir/grafana")
            self._cuisine.core.file_copy("/usr/share/grafana/", "$appDir/", recursive=True)

        else:
            raise RuntimeError("platform not supported")

        if self._cuisine.core.file_exists("/usr/share/grafana/conf/defaults.ini"):
            cfg = self._cuisine.core.file_read("/usr/share/grafana/conf/defaults.ini")
        else:
            cfg = self._cuisine.core.file_read('$tmpDir/cfg/grafana/conf/defaults.ini')
        self._cuisine.core.file_write('$cfgDir/grafana/grafana.ini', cfg)

    # def build(self, start=True, influx_addr='127.0.0.1', influx_port=8086, port=3000):
    #     if start:
    #         self.start(influx_addr=influx_addr, influx_port=influx_port, port=port)

    def start(self, influx_addr='127.0.0.1', influx_port=8086, port=3000):

        cmd = "cd $appDir/grafana && $binDir/grafana-server --config=$cfgDir/grafana/grafana.ini\n"
        cmd = self._cuisine.core.args_replace(cmd)
        self._cuisine.core.file_write("/opt/jumpscale8/bin/start_grafana.sh", cmd, 777, replaceArgs=True)
        self._cuisine.process.kill("grafana-server")
        self._cuisine.processmanager.ensure(
            "grafana-server", cmd=cmd, env={})
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

    def scriptedAgent(self):
        # TODO: *2 dont understand this please document
        scriptedagent = """
        /* global _ */
        /*
         * Complex scripted dashboard
         * This script generates a dashboard object that Grafana can load. It also takes a number of user
         * supplied URL parameters (in the ARGS variable)
         *
         * Return a dashboard object, or a function
         *
         * For async scripts, return a function, this function must take a single callback function as argument,
         * call this callback function with the dashboard object (look at scripted_async.js for an example)
         */

        'use strict';

        // accessible variables in this scope
        var window, document, ARGS, $, jQuery, moment, kbn;

        // Setup some variables
        var dashboard;

        // All url parameters are available via the ARGS object
        var ARGS;

        // Intialize a skeleton with nothing but a rows array and service object
        dashboard = {
          rows : [],
          refresh: '5s',
        };

        // Set a title
        dashboard.title = 'Scripted dash';

        // Set default time
        // time can be overriden in the url using from/to parameters, but this is
        // handled automatically in grafana core during dashboard initialization
        dashboard.time = {
          from: "now-6h",
          to: "now"
        };

        var series = [];

        if(!_.isUndefined(ARGS.series)) {
          series = ARGS.series.split(',');
        }


        dashboard.rows.push({
            panels: [
        {
          "aliasColors": {},
          "bars": false,
          "datasource": 'influxdb_main',
          "editable": true,
          "error": false,
          "fill": 1,
          "grid": {
            "leftLogBase": 1,
            "leftMax": null,
            "leftMin": null,
            "rightLogBase": 1,
            "rightMax": null,
            "rightMin": null,
            "threshold1": null,
            "threshold1Color": "rgba(216, 200, 27, 0.27)",
            "threshold2": null,
            "threshold2Color": "rgba(234, 112, 112, 0.22)"
          },
          "hideTimeOverride": false,
          "id": 1,
          "isNew": true,
          "legend": {
            "avg": false,
            "current": false,
            "max": false,
            "min": false,
            "show": true,
            "total": false,
            "values": false
          },
          "lines": true,
          "linewidth": 2,
          "links": [],
          "nullPointMode": "connected",
          "percentage": false,
          "pointradius": 5,
          "points": false,
          "renderer": "flot",
          "seriesOverrides": [],
          "span": 12,
          "stack": false,
          "steppedLine": false,
          "targets": series.map(function(x){return {
              "dsType": "influxdb",
              "groupBy": [
                {
                  "params": [
                    "auto"
                  ],
                  "type": "time"
                },
                {
                  "params": [
                    "null"
                  ],
                  "type": "fill"
                }
              ],
              "hide": false,
              "measurement": x,
              "query": 'SELECT "value" FROM "'+x+'"',
              "rawQuery": true,
              "refId": "A",
              "resultFormat": "time_series",
              "select": [
                [
                  {
                    "params": [
                      "value"
                    ],
                    "type": "field"
                  },
                  {
                    "params": [],
                    "type": "mean"
                  }
                ]
              ],
              "tags": []
            }
          }),
          "timeFrom": null,
          "timeShift": null,
          "title": "Panel Title",
          "tooltip": {
            "shared": true,
            "value_type": "cumulative"
          },
          "type": "graph",
          "x-axis": true,
          "y-axis": true,
          "y_formats": [
            "short",
            "short"
          ]
        }
            ]
        });


        return dashboard;

        """

        self._cuisine.core.file_write('$tmplsDir/cfg/grafana/public/dashboards/scriptedagent.js', scriptedagent)
