<!-- toc -->
## j.core.platformtype.myplatform.executor.cuisine.apps.dnsmasq

- /opt/jumpscale8/lib/JumpScale/sal/dnsmasq/Dnsmasq.py
- Properties
    - executor
    - logger

### Methods

#### addHost(*macaddress, ipaddress, name*) 

```
Add a host.

@param macaddress string: macaddress
@param ip string: ip
@param name string: name

```

#### config(*device='eth0', rangefrom='', rangeto='', deviceonly=True*) 

```
if rangefrom & rangeto not specified then will serve full local range minus bottomn 10 &
    top 10 addr

```

#### install(*start=True*) 

```
Install Dnsmasq.

@param start=True: start dnsmasq

```

#### removeHost(*macaddress*) 

```
Removes a dhcp-host entry from dnsmasq.conf file

```

#### restart() 

```
Restarts Dnsmasq.

```

#### setConfigPath(*config_path*) 

```
Set configuration files path.

@param config_path string: configuration file path.

```

