## BindDNS

`j.sal.bind` helps you with many tasks related to Bind9 service.


### Usage

* Starting

```py
j.sal.bind.start()
```

* Stopping

```py
j.sal.bind.stop()
```

* Restarting

```py
j.sal.bind.restart()
```

* Update the IP of a host

```py
j.sal.bind.updateHostIp(host, ip)
```

* Add a record

```py
addRecord(self, domain, host, ip, klass, type, ttl)
```

* Delete a host

```py
deleteHost(host)
```

* Listing all zones

```py
j.sal.bind.zones
```

* map of available zones

```py
j.sal.bind..map
```

* a reverse map of available zones

```py
j.sal.bind.reversemap
```