# Openvswitch

```
j.sal.openvswitch
```

## This library enables the user to configure the network by doing the followig:

- Creating a new bridge, vlan bridge and vxlan bridge

```python
j.sal.openvswitch.newBridge(name, interface)
j.sal.openvswitch.newVlanBridge(name, parentbridge, vlanid, mtu)
    # mtu is an optional variable which defines the Maximum Transmission Unit of the new Vlan Bridge with a default of 1500
j.sal.openvswitch.createVXLanBridge(networkid, backend, bridgename)
```

- Configuring an interface with a static address

```python
j.sal.openvswitch.configureStaticAddress(interfacename, ipaddr, gateway)
```

- Get an interface type from its name

```python
j.sal.openvswitch.getType()
```

- Resetting of an interface to the default configurations

```python
j.sal.openvswitch.initNetworkInterfaces()
```

- Creating a new bonded backplane

```python
j.sal.openvswitch.newBondedBackplane(name, interfaces, trunks):
```

- Setting and configuring a backplane

```python
j.sal.openvswitch.setBackplane(interfacename, backplanename, ipaddr, gateway)
j.sal.openvswitch.setBackplaneDhcp(interfacename, backplanename)
j.sal.openvswitch.setBackplaneNoAddress(interfacename, backplanename)
j.sal.openvswitch.setBackplaneNoAddressWithBond(bondname, bondinterfaces, backplanename)
j.sal.openvswitch.setBackplaneWithBond(bondname, bondinterfaces, backplanename, ipaddr, gateway)
```

- Get all network configurations from the system

```python
j.sal.openvswitch.getConfigFromSystem(reload)
    # reload is an optional boolean variable
```

```
!!!
title = "OpenVSwitch"
date = "2017-04-08"
tags = []
```
