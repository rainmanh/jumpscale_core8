<!-- toc -->
## j.tools.develop

- /opt/jumpscale8/lib/JumpScale/tools/develop/DevelopTools.py

### Methods

#### help() 

#### init(*nodes*) 

```
define which nodes to init,
format = ["localhost", "ovh4", "anode:2222", "192.168.6.5:23"]
this will be remembered in local redis for further usage

format can also be a string e.g. ovh4,ovh3:2022

```

#### monitorChanges(*sync=True, reset*) 

```
look for changes in directories which are being pushed & if found push to remote nodes

```

#### resetState() 

#### syncCode(*ask, monitor, rsyncdelete=True, reset*) 

```
sync all code to the remote destinations

@param reset=True, means we remove the destination first
@param ask=True means ask which repo's to sync (will get remembered in redis)

```


```
!!!
title = "J.tools.develop"
date = "2017-04-08"
tags = []
```

```
!!!
title = "J.tools.develop"
date = "2017-04-08"
tags = []
```

```
!!!
title = "J.tools.develop"
date = "2017-04-08"
tags = []
```
