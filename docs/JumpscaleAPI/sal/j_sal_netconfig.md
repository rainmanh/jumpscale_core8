<!-- toc -->
## j.sal.netconfig

- /opt/jumpscale8/lib/JumpScale/sal/netconfig/Netconfig.py
- Properties
    - root
    - log

### Methods

Helps you to configure the network.

#### chroot(*root*) 

```
choose another root to manipulate the config files
@param root str: new root path for config files.

```

#### hostname_set(*hostname*) 

```
change hostname
@param hostname str: new hostname.

```

#### interface_configure(*dev, ipaddr, bridgedev, gw, dhcp, apply=True*) 

```
ipaddr in form of 192.168.10.2/24 (can be list)
gateway in form of 192.168.10.254

```

#### interface_configure_bridge_safe(*interface, ipaddr, gw, mask*) 

```
will in a safe way configure bridge brpub
if available and has ip addr to go to internet then nothing will happen
otherwise system will try in a safe way set this ipaddr, this is a dangerous operation

if ipaddr is None then will look for existing config on interface and use that one to
    configure the bridge

```

#### interface_configure_dhcp(*dev='eth0', apply=True*) 

```
Configure interface to use dhcp
@param dev str: interface name.

```

#### interface_configure_dhcp_bridge(*dev='eth0', bridgedev, apply=True*) 

#### interface_configure_dhcp_waitdown(*interface='eth0', ipaddr, gw, mask=24, config=True*) 

```
Bringing all bridges down and set specified interface with an IP address or on dhcp if no
    IP address, is provided
@param config if True then will be stored in linux configuration files

```

#### interface_configure_dhcp_waitdown2(*interface='eth0'*) 

```
this will bring all bridges down and set specified interface on dhcp (dangerous)

```

#### interface_remove(*dev, apply=True*) 

```
Remove an interface.

```

#### interface_remove_ipaddr(*network='192.168.1'*) 

#### interfaces_reset(*shutdown*) 

```
empty config of /etc/network/interfaces
@param shutdown bool: shutsdown the network.

```

#### interfaces_restart(*dev*) 

```
Restart an interface
@param dev str: interface name.

```

#### interfaces_shutdown(*excludes*) 

```
find all interfaces and shut them all down with ifdown
this is to remove all networking things going on
@param excludes list: excluded interfaces.

```

#### nameserver_set(*addr*) 

```
Set nameserver
@param addr string: nameserver address.
resolvconf will be disabled

```

#### proxy_enable() 


```
!!!
title = "J Sal Netconfig"
date = "2017-04-08"
tags = []
```

```
!!!
title = "J Sal Netconfig"
date = "2017-04-08"
tags = []
```

```
!!!
title = "J Sal Netconfig"
date = "2017-04-08"
tags = []
```
