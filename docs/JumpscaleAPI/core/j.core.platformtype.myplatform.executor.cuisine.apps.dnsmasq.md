<!-- toc -->
## j.core.platformtype.myplatform.executor.cuisine.apps.dnsmasq

- /opt/jumpscale8/lib/JumpScale/sal/dnsmasq/Dnsmasq.py
- Properties
    - logger
    - cuisine
    - executor

### Methods

#### addHost(*macaddress, ipaddress, name*) 

#### config(*device='eth0', rangefrom='', rangeto='', deviceonly=True*) 

```
if rangefrom & rangeto not specified then will serve full local range minus bottomn 10 &
    top 10 addr

```

#### install(*start=True*) 

#### removeHost(*macaddress*) 

```
Removes a dhcp-host entry from dnsmasq.conf file

```

#### restart() 

#### setConfigPath(*config_path*) 

