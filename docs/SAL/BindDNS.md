# BindDNS

`j.sal.bind` helps you with many tasks related to Bind9 service.

## Usage

- Starting bind9 server 

```python
j.sal.bind.start()
```

- Stopping bind9 server

```python
j.sal.bind.stop()
```

- Restarting bind9 server 

```python
j.sal.bind.restart()
```

- Update the IP of a host

```python
j.sal.bind.updateHostIp(host, ip)
```

- Add an A record

```python
addRecord(self, domain, host, ip, klass, type, ttl)
```

- Delete a host

```python
deleteHost(host)
```

- Listing all zones

```python
j.sal.bind.zones
```

- map of available zones

```python
j.sal.bind..map
```

- a reverse map of available zones

```python
j.sal.bind.reversemap
```
