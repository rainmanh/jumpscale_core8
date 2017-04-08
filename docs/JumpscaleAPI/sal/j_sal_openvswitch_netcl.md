<!-- toc -->
## j.sal.openvswitch.netcl

- /opt/jumpscale8/lib/JumpScale/sal/openvswitch/VXNet/netclasses.py
- Properties
    - destroyVethPair
    - get_all_ifaces
    - addIPv6
    - vsctl
    - connectIfToNameSpace
    - ofctl
    - get_all_namespaces
    - limit_interface_rate
    - listBridgePorts
    - setMTU
    - destroyVXlan
    - NameSpace
    - disable_ipv6
    - addIPv4
    - VXlan
    - VXBridge
    - destroyBridge
    - addVlanPatch
    - get_all_bridges
    - doexec
    - j
    - sys
    - command_name
    - os
    - NetID
    - ip_link_set
    - addBond
    - dobigexec
    - VXNameSpace
    - send_to_syslog
    - Bridge
    - BondBridge
    - time
    - connectIfToBridge
    - removeIfFromBridge
    - destroyNameSpace
    - ethtool
    - createVethPair
    - VlanPatch
    - ip
    - createBridge
    - PHYSMTU
    - createNameSpace
    - createVXlan
    - VethPair
    - subprocess

### Methods

#### VlanPatch(*parentbridge, vlanbridge, vlanid*) 

#### addBond(*bridge, bondname, iflist, lacp='active', lacp_time='fast', mode='balance-tcp', trunks*) 

```
Add a bond to a bridge
:param bridge: BridgeName (string)
:param bondname: Bondname (string)
:param iflist: list or tuple
:param lacp: "active" or "passive"
:param lacp_time: mode "fast" or "slow"
:param mode: balance-tcp, balance-slb, active-passive
:param trunks: allowed VLANS (list or tuple)

```

#### addIPv4(*interface, ipobj, namespace*) 

#### addIPv6(*interface, ipobj, namespace*) 

#### addVlanPatch(*parbr, vlbr, id, mtu*) 

#### connectIfToBridge(*bridge, interfaces*) 

#### connectIfToNameSpace(*nsname, interface*) 

#### createBridge(*name*) 

#### createNameSpace(*name*) 

#### createVXlan(*vxname, vxid, multicast, vxbackend*) 

```
Always brought up too
Created with no protocol, and upped (no ipv4, no ipv6)
Fixed standard : 239.0.x.x, id
# 0000-fe99 for customer vxlans, ff00-ffff for environments
MTU of VXLAN = 1500

```

#### createVethPair(*left, right*) 

#### destroyBridge(*name*) 

#### destroyNameSpace(*name*) 

#### destroyVXlan(*name*) 

#### destroyVethPair(*left*) 

#### disable_ipv6(*interface*) 

#### dobigexec(*args*) 

```
Execute a subprocess, then return its return code, stdout and stderr

```

#### doexec(*args*) 

```
Execute a subprocess, then return its return code, stdout and stderr

```

#### get_all_bridges() 

#### get_all_ifaces() 

```
List of network interfaces
@rtype : dict

```

#### get_all_namespaces() 

#### ip_link_set(*device, args*) 

#### limit_interface_rate(*limit, interface, burst*) 

#### listBridgePorts(*name*) 

#### removeIfFromBridge(*bridge, interfaces*) 

#### send_to_syslog(*msg*) 

#### setMTU(*interface, mtu*) 


```
!!!
title = "J Sal Openvswitch Netcl"
date = "2017-04-08"
tags = []
```

```
!!!
title = "J Sal Openvswitch Netcl"
date = "2017-04-08"
tags = []
```

```
!!!
title = "J Sal Openvswitch Netcl"
date = "2017-04-08"
tags = []
```
