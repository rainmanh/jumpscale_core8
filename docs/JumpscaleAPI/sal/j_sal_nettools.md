<!-- toc -->
## j.sal.nettools

- /opt/jumpscale8/lib/JumpScale/sal/nettools/NetTools.py
- Properties
    - logger

### Methods

#### bridgeExists(*bridgename*) 

#### checkIpAddressIsLocal(*ipaddr*) 

#### checkListenPort(*port*) 

```
Check if a certain port is listening on the system.

@param port: sets the port number to check
@return status: 0 if running 1 if not running

```

#### checkUrlReachable(*url, timeout=5*) 

```
raise operational critical if unreachable
return True if reachable

```

#### download(*url, localpath, username, passwd, overwrite=True*) 

```
Download a url to a file or a directory, supported protocols: http, https, ftp, file
@param url: URL to download from
@type url: string
@param localpath: filename or directory to download the url to pass - to return data
@type localpath: string
@param username: username for the url if it requires authentication
@type username: string
@param passwd: password for the url if it requires authentication
@type passwd: string

```

#### downloadIfNonExistent(*url, destination_file_path, md5_checksum, http_auth_username, http_auth_password*) 

```
Downloads the file from the specified url to the specified destination if it is not
    already there
or if the target file checksum doesn't match the expected checksum.

```

#### getDefaultIPConfig() 

#### getDefaultRouter() 

```
Get default router
@rtype: string representing the router interface

```

#### getDomainName() 

```
Retrieve the dns domain name

```

#### getHostByName(*dnsHostname*) 

#### getHostname() 

```
Get hostname of the machine

```

#### getIpAddress(*interface*) 

```
Return a list of ip addresses and netmasks assigned to this interface

```

#### getIpAddresses(*up*) 

#### getMacAddress(*interface*) 

```
Return the MAC address of this interface

```

#### getMacAddressForIp(*ipaddress*) 

```
Search the MAC address of the given IP address in the ARP table

@param ipaddress: IP address of the machine
@rtype: string
@return: The MAC address corresponding with the given IP
@raise: RuntimeError if no MAC found for IP or if platform is not suppported

```

#### getNameServer() 

```
Returns the first nameserver IP found in /etc/resolv.conf

Only implemented for Unix based hosts.

@returns: Nameserver IP
@rtype: string

@raise NotImplementedError: Non-Unix systems
@raise RuntimeError: No nameserver could be found in /etc/resolv.conf

```

#### getNetworkInfo() 

```
returns \{macaddr_name:[ipaddr,ipaddr],...\}

REMARK: format changed because there was bug which could not work with bridges

TODO: change for windows

```

#### getNicType(*interface*) 

```
Get Nic Type on a certain interface
@param interface: Interface to determine Nic type on
@raise RuntimeError: On linux if ethtool is not present on the system

```

#### getNics(*up*) 

```
Get Nics on this machine
Works only for Linux/Solaris systems
@param up: only returning nics which or up

```

#### getReachableIpAddress(*ip, port*) 

```
Returns the first local ip address that can connect to the specified ip on the specified
    port

```

#### getVlanTag(*interface, nicType*) 

```
Get VLan tag on the specified interface and vlan type

```

#### getVlanTagFromInterface(*interface*) 

```
Get vlan tag from interface
@param interface: string interface to get vlan tag on
@rtype: integer representing the vlan tag

```

#### isIpLocal(*ipaddress*) 

#### isNicConnected(*interface*) 

#### pingMachine(*ip, pingtimeout=60, recheck, allowhostname=True*) 

```
Ping a machine to check if it's up/running and accessible
@param ip: Machine Ip Address
@param pingtimeout: time in sec after which ip will be declared as unreachable
@param recheck: Unused, kept for backwards compatibility
@param allowhostname: allow pinging on hostname (default is false)
@rtype: True if machine is pingable, False otherwise

```

#### pm_formatMacAddress(*macaddress*) 

#### resetDefaultGateway(*gw*) 

#### tcpPortConnectionTest(*ipaddr, port, timeout*) 

#### validateIpAddress(*ipaddress*) 

```
Validate wether this ip address is a valid ip address of 4 octets ranging from 0 to 255 or
    not
@param ipaddress: ip address to check on
@rtype: boolean...True if this ip is valid, False if not

```

#### waitConnectionTest(*ipaddr, port, timeout*) 

```
will return false if not successfull (timeout)

```

#### waitConnectionTestStopped(*ipaddr, port, timeout*) 

```
will test that port is not active
will return false if not successfull (timeout)

```


```
!!!
title = "J Sal Nettools"
date = "2017-04-08"
tags = []
```

```
!!!
title = "J Sal Nettools"
date = "2017-04-08"
tags = []
```

```
!!!
title = "J Sal Nettools"
date = "2017-04-08"
tags = []
```
