# NetTools

```python
j.sal.nettools
```

## This library contains all related information of the network and enables the user to do the followig:

- Check if an IP address is local on the network

```python
j.sal.nettools.checkIpAddressIsLocal(ipaddr)
```

- Check if a certain port is listening on the system

```python
j.sal.nettools.checkListenPort(port)
```

- Check if a url is reachable

```python
j.sal.nettools.checkUrlReachable(url)
```

- Get information about the network

```python
j.sal.nettools.getNetworkInfo()
j.sal.nettools.getDefaultIPConfig()
j.sal.nettools.getDefaultRouter()
j.sal.nettools.getDomainName()
j.sal.nettools.getHostname()
j.sal.nettools.getNameServer()
j.sal.nettools.getNicType(interface)
j.sal.nettools.getHostByName(Hostname)
j.sal.nettools.getMacAddress(interface)
j.sal.nettools.getNics(up=False)
j.sal.nettools.getReachableIpAddress(ip, port) #Returns the first local ip address that can connect to the specified ip & port
j.sal.nettools.getVlanTag(interface, nicType=None) #Get VLan tag on the specified interface and type
```

- Ping a machine to check if it's up/running and accessible

```python
j.sal.nettools.pingMachine(ip, pingtimeout=60, recheck=False, allowhostname=True)
```

- Reset the default gateway of the network

```python
j.sal.nettools.resetDefaultGateway(gw)
```

Validate wether this ip address is a valid ip address of 4 octets ranging from 0 to 255 or not

```python
j.sal.nettools.validateIpAddress(ipaddress)
```
