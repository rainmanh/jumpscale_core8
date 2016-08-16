from JumpScale import j
CONFIG="""
reporting-disabled = false

[meta]
  dir = "$vardir/influxdb/meta"
  hostname = "localhost"
  bind-address = ":8088"
  retention-autocreate = true
  election-timeout = "1s"
  heartbeat-timeout = "1s"
  leader-lease-timeout = "500ms"
  commit-timeout = "50ms"
  cluster-tracing = false

[data]
  dir = "$vardir/influxdb/data"
  engine = "bz1"
  max-wal-size = 104857600
  wal-flush-interval = "10m0s"
  wal-partition-flush-delay = "2s"
  wal-dir = "$vardir/influxdb/wal"
  wal-logging-enabled = true
  wal-ready-series-size = 30720
  wal-compaction-threshold = 0.5
  wal-max-series-size = 1048576
  wal-flush-cold-interval = "5s"
  wal-partition-size-threshold = 20971520

[cluster]
  force-remote-mapping = false
  write-timeout = "5s"
  shard-writer-timeout = "5s"
  shard-mapper-timeout = "5s"

[retention]
  enabled = true
  check-interval = "10m0s"

[shard-precreation]
  enabled = true
  check-interval = "10m0s"
  advance-period = "30m0s"

[admin]
  enabled = true
  bind-address = ":8083"
  https-enabled = false
  https-certificate = "/etc/ssl/influxdb.pem"

[monitor]
  store-enabled = false
  store-database = "_internal"
  store-interval = "10s"

[http]
  enabled = true
  bind-address = ":8086"
  auth-enabled = false
  log-enabled = true
  write-tracing = false
  pprof-enabled = false
  https-enabled = false
  https-certificate = "/etc/ssl/influxdb.pem"

[collectd]
  enabled = false
  bind-address = ":25826"
  database = "collectd"
  retention-policy = ""
  batch-size = 1000
  batch-pending = 5
  batch-timeout = "10s"
  typesdb = "/usr/share/collectd/types.db"

[opentsdb]
  enabled = false
  bind-address = ":4242"
  database = "opentsdb"
  retention-policy = ""
  consistency-level = "one"
  tls-enabled = false
  certificate = "/etc/ssl/influxdb.pem"
  batch-size = 1000
  batch-pending = 5
  batch-timeout = "1s"

[continuous_queries]
  log-enabled = true
  enabled = true
  recompute-previous-n = 2
  recompute-no-older-than = "10m0s"
  compute-runs-per-interval = 10
  compute-no-more-than = "2m0s"

[hinted-handoff]
  enabled = true
  dir = "/root/.influxdb/hh"
  max-size = 1073741824
  max-age = "168h0m0s"
  retry-rate-limit = 0
  retry-interval = "1s"

"""

class MockInflux(object):
    def mockinstall(self):
        j.do.pullGitRepo(url = 'https://git.aydo.com/binary/influxdb_bin.git')
        j.sal.fs.createDir('/opt/influxdb')

        src='/opt/code/git/binary/influxdb_bin'
        dst='/opt/influxdb/'
        j.do.copyFile(src,"/opt/influxdb/",skipIfExists=True) 
        j.sal.fs.changeDir('/opt/influxdb')
     #   return True

    # def config(self):
        j.sal.fs.createDir("/opt/influxdb/cfg")   
        cfg = j.dirs.replaceTxtDirVars(CONFIG, additionalArgs={})
        j.sal.fs.createEmptyFile('config.toml')
        j.do.writeFile("/opt/influxdb/cfg/config.toml", cfg)
      #  return True

    # def run(self):
        j.sal.process.execute('./influxd -config=cfg/config.toml', die=True, outputToStdout=True ) 
        return True

if __name__ == '__main__':
    mock = MockInflux()
    mock.mockinstall()
    #mock.config()
    #mock.run()
