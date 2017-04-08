<!-- toc -->
## j.servers.geventws

- /opt/jumpscale8/lib/JumpScale/servers/geventws/GeventWSFactory.py
- Properties
    - cache
    - cachecat

### Methods

#### getClient(*addr, port, category='core', org='myorg', user='root', passwd='passwd', ssl, roles, id, timeout=60*) 

#### getHAClient(*connections, category='core', org='myorg', user='root', passwd='passwd', ssl, roles, id, timeout=60, reconnect*) 

#### getServer(*port, sslorg, ssluser, sslkeyvaluestor*) 

```
HOW TO USE:
daemon=j.servers.geventws.getServer(port=4444)

class MyCommands:
    def __init__(self,daemon):
        self.daemon=daemon

    #session always needs to be there
    def pingcmd(self,session=session):
        return "pong"

    def echo(self,msg="",session=session):
        return msg

daemon.addCMDsInterface(MyCommands,category="optional")  #pass as class not as object !!!
    chose category if only 1 then can leave ""

daemon.start()

```

#### initSSL4Server(*organization, serveruser, sslkeyvaluestor*) 

```
use this to init your ssl keys for the server (they can be used over all transports)

```


```
!!!
title = "J Servers Geventws"
date = "2017-04-08"
tags = []
```

```
!!!
title = "J Servers Geventws"
date = "2017-04-08"
tags = []
```

```
!!!
title = "J Servers Geventws"
date = "2017-04-08"
tags = []
```
