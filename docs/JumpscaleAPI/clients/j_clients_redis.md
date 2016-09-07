<!-- toc -->
## j.clients.redis

- /opt/jumpscale8/lib/JumpScale/clients/redis/Redis.py

### Methods

    

#### configureInstance(*name, ip='localhost', port=6379, maxram=200, appendonly=True, snapshot, slave, ismaster, passwd, unixsocket*) 

```
@param maxram = MB of ram
slave example: (192.168.10.10,8888,asecret)   (ip,port,secret)

```

#### deleteInstance(*name*) 

#### emptyInstance(*name*) 

#### get(*ipaddr, port, password='', fromcache=True*) 

#### getByInstance(*instance*) 

#### getInstance(*cuisine*) 

#### getPort(*name*) 

#### getQueue(*ipaddr, port, name, namespace='queues', fromcache=True*) 

#### isRunning(*name='', ip_address='localhost', port=6379, path='$binDir'*) 

