<!-- toc -->
## j.tools.perftesttools

- /opt/jumpscale8/lib/JumpScale/tools/perftesttools/PerfTestToolsFactory.py
- Properties
    - monitorNodeSSHPort
    - redispasswd
    - monitorNodeIp
    - sshkey
    - nodes

### Methods

j.tools.perftesttools.getNodeMonitor("localhost",22)
make sure there is influxdb running on monitor node (root/root)
make sure there is redis running on monitor node with passwd as specified

for example script
call self.getScript()

#### getExampleScript(*path*) 

#### getNodeBase(*ipaddr, sshport=22, name=''*) 

#### getNodeHost(*ipaddr, sshport=22, name=''*) 

#### getNodeMonitor(*name=''*) 

#### getNodeNAS(*ipaddr, sshport=22, nrdisks, fstype='xfs', role='', debugdisk='', name=''*) 

```
@param debug when True it means we will use this for development purposes & not init &
    mount local disks

```

#### influxpump() 

```
will dump redis stats into influxdb & env is used to get config parameters from
influxdb is always on localhost & std login/passwd

```

#### init(*testname, monitorNodeIp, sshPort, redispasswd='', sshkey*) 

```
sshkey can be path to key or the private key itself
the goal is you use ssh-agent & your keys pre-loaded, best not to manually work with keys
    !!!

```

#### monitor() 

```
will do monitoring & send results to redis, env is used to get config parameters from

```


```
!!!
title = "J.tools.perftesttools"
date = "2017-04-08"
tags = []
```

```
!!!
title = "J.tools.perftesttools"
date = "2017-04-08"
tags = []
```

```
!!!
title = "J.tools.perftesttools"
date = "2017-04-08"
tags = []
```
