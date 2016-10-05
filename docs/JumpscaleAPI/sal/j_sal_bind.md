<!-- toc -->
## j.sal.bind

- /opt/jumpscale8/lib/JumpScale/sal/bind/BindDNS.py
- Properties
    - logger

### Methods

#### addRecord(*domain, host, ip, klass, type, ttl*) 

```
Add an A record.

@param domain string: domain
@param host string: host
@param ip string: ip
@param klass string: class
@param type:
@param ttl: time to live

```

#### cleanCache() 

#### deleteHost(*host*) 

```
Delete host.

@param host string: host

```

#### restart() 

```
Restart bind9 server.

```

#### start() 

```
Start bind9 server.

```

#### stop() 

```
Stop bind9 server.

```

#### updateHostIp(*host, ip*) 

```
Update the IP of a host.

@param host string: hostname
@param ip   string: ip

```

