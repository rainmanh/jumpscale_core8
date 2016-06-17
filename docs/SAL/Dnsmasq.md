# DNSmasq
```
j.sal.dnsmasq
```
##This library enables the user to install and configure the Dnsmasq service by doing the following:

* Installing Dnsmasq.
```
j.sal.dnsmasq.install(start=True)
```
* Restarting Dnsmasq.
```
j.sal.dnsmasq.restart()
```
* Adding or removing a dhcp-host entry to dnsmasq.conf file.
```
j.sal.dnsmasq.addHost(macaddress, ipaddress, name=None)
j.sal.dnsmasq.removeHost(macaddress)
```
* Set configuration files path.
```
j.sal.dnsmasq.setConfigPath(config_path=None)
``
* Configuring dnsmasq on interfaces.
```
j.sal.dnsmasq.config(interface="eth0",rangefrom="",rangeto="",deviceonly=True)
```