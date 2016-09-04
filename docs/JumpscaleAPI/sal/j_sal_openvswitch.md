<!-- toc -->
## j.sal.openvswitch

- /opt/jumpscale8/lib/JumpScale/sal/openvswitch/NetConfigFactory.py
- Properties
    - PHYSMTU

### Methods

#### applyconfig(*interfacenameToExclude, backplanename*) 

```
DANGEROUS, will remove old configuration

```

#### configureStaticAddress(*interfacename='eth0', ipaddr='192.168.10.10/24', gw*) 

```
Configure a static address

```

#### createVXLanBridge(*networkid, backend, bridgename*) 

```
Creates a proper vxlan interface and bridge based on a backplane

```

#### ensureVXNet(*networkid, backend*) 

#### getConfigFromSystem(*reload*) 

```
walk over system and get configuration, result is dict

```

#### getType(*interfaceName*) 

#### initNetworkInterfaces() 

```
Resets /etc/network/interfaces with a basic configuration

```

#### newBondedBackplane(*name, interfaces, trunks*) 

```
Reasonable defaults  : mode=balance-tcp, lacp=active,fast, bondname=brname-Bond, all vlans
    allowed

```

#### newBridge(*name, interface*) 

```
@param interface interface where to connect this bridge to

```

#### newVlanBridge(*name, parentbridge, vlanid, mtu*) 

#### printConfigFromSystem() 

#### removeOldConfig() 

#### setBackplane(*interfacename='eth0', backplanename=1, ipaddr='192.168.10.10/24', gw=''*) 

```
DANGEROUS, will remove old configuration

```

#### setBackplaneDhcp(*interfacename='eth0', backplanename='Public'*) 

```
DANGEROUS, will remove old configuration

```

#### setBackplaneNoAddress(*interfacename='eth0', backplanename=1*) 

```
DANGEROUS, will remove old configuration

```

#### setBackplaneNoAddressWithBond(*bondname, bondinterfaces, backplanename='backplane'*) 

```
DANGEROUS, will remove old configuration

```

#### setBackplaneWithBond(*bondname, bondinterfaces, backplanename='backplane', ipaddr='192.168.10.10/24', gw=''*) 

```
DANGEROUS, will remove old configuration

```

