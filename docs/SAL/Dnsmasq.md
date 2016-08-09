# DNSmasq

```python
j.sal.dnsmasq
```

# This library enables the user to install and configure the Dnsmasq service by doing the following:

- Installing Dnsmasq

```python
j.sal.dnsmasq.install(start=True)
```

- Restarting Dnsmasq

```python
j.sal.dnsmasq.restart()
```

- Adding or removing a dhcp-host entry to dnsmasq.conf file

```python
j.sal.dnsmasq.addHost(macaddress, ipaddress, name=None)
j.sal.dnsmasq.removeHost(macaddress)
```

- Set configuration files path

```python
j.sal.dnsmasq.setConfigPath(config_path=None)
```

- Configuring dnsmasq on interfaces

```python
j.sal.dnsmasq.config(interface="eth0",rangefrom="",rangeto="",deviceonly=True)
```
