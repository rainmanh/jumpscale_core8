# BindDNS

`j.sal.bind` helps you with many tasks related to bind9 service.


## Usage
* Starting
```
j.sal.bind.start()
```
* Stopping
```
j.sal.bind.stop()
```
* Restarting
```
j.sal.bind.restart()
```
* Update the IP of a host
```
j.sal.bind.updateHostIp(host, ip)
```
* Add a record
```
addRecord(self, domain, host, ip, klass, type, ttl)
```
* Delete a host
```
deleteHost(host)
```
* Listing all zones
```
j.sal.bind.zones
```

* map of available zones
```
j.sal.bind..map
```

* a reverse map of available zones
```
j.sal.bind.reversemap
```
