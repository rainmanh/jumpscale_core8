<!-- toc -->
## j.sal.netconfig

- /opt/jumpscale8/lib/JumpScale/sal/netconfig/Netconfig.py
- Properties
    - root

### Methods

    

#### chroot(*root*) 

```
choose another root to manipulate the config files

```

#### hostname_set(*hostname*) 

```
change hostname

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

if ipaddr == None then will look for existing config on interface and use that one to
    configure the bridge

```

#### interface_configure_dhcp(*dev='eth0', apply=True*) 

#### interface_configure_dhcp_bridge(*dev='eth0', bridgedev, apply=True*) 

#### interface_configure_dhcp_waitdown(*interface='eth0'*) 

```
this will bring all bridges down and set specified interface on dhcp (dangerous)

```

#### interface_remove(*dev, apply=True*) 

#### interface_remove_ipaddr(*network='192.168.1'*) 

#### interfaces_reset(*shutdown*) 

```
empty config of /etc/network/interfaces

```

#### interfaces_restart(*dev*) 

#### interfaces_shutdown(*excludes*) 

```
find all interfaces and shut them all down with ifdown
this is to remove all networking things going on

```

#### nameserver_set(*addr*) 

```
resolvconf will be disabled

```

#### proxy_enable(**) 

