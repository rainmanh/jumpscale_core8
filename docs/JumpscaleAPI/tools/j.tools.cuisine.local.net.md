<!-- toc -->
## j.tools.cuisine.local.net

- /opt/jumpscale8/lib/JumpScale/tools/cuisine/CuisineNet.py

### Methods

#### findNodesSSH(*range, ips*) 

```
@param range in format 192.168.0.0/24

if range not specified then will take all ranges of local ip addresses (nics)
find nodes which are active around (answer on SSH)

```

#### getInfo(*device*) 

```
returns network info like

[\{'cidr': 8, 'ip': ['127.0.0.1'], 'mac': '00:00:00:00:00:00', 'name': 'lo'\},
 \{'cidr': 24,
  'ip': ['192.168.0.105'],
  'mac': '80:ee:73:a9:19:05',
  'name': 'enp2s0'\},
 \{'cidr': 0, 'ip': [], 'mac': '80:ee:73:a9:19:06', 'name': 'enp3s0'\},
 \{'cidr': 16,
  'ip': ['172.17.0.1'],
  'mac': '02:42:97:63:e6:ba',
  'name': 'docker0'\}]

```

#### getNetObject(*device*) 

#### getNetRange(*device, skipBegin=10, skipEnd=10*) 

```
return ($fromip,$topip) from range attached to device, skip the mentioned ip addresses

```

#### netconfig(*interface, ipaddr, cidr=24, gateway, dns='8.8.8.8', masquerading*) 

#### ping(*host*) 

#### setInterfaceFile(*ifacefile, pinghost='www.google.com'*) 

```
will set interface file, if network access goes away then will restore previous one

```


```
!!!
title = "J.tools.cuisine.local.net"
date = "2017-04-08"
tags = []
```

```
!!!
title = "J.tools.cuisine.local.net"
date = "2017-04-08"
tags = []
```

```
!!!
title = "J.tools.cuisine.local.net"
date = "2017-04-08"
tags = []
```
