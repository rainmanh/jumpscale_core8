## DNSmasq

```py
j.sal.dnsmasq
```

## This library enables the user to install and configure the Dnsmasq service by doing the following:

* Installing Dnsmasq

```py
j.sal.dnsmasq.install(start=True)
```

* Restarting Dnsmasq

```py
j.sal.dnsmasq.restart()
```

* Adding or removing a dhcp-host entry to dnsmasq.conf file

```py
j.sal.dnsmasq.addHost(macaddress, ipaddress, name=None)
j.sal.dnsmasq.removeHost(macaddress)
```

* Set configuration files path

```py
j.sal.dnsmasq.setConfigPath(config_path=None)
```

* Configuring dnsmasq on interfaces

```py
j.sal.dnsmasq.config(interface="eth0",rangefrom="",rangeto="",deviceonly=True)
```