<!-- toc -->
## j.tools.cuisine

- /opt/jumpscale8/lib/JumpScale/tools/cuisine/CuisineFactory.py
- Properties
    - logger

### Methods

#### authorizeKey(*addr='localhost:22', login='root', passwd='', keyname='', pubkey='', passphrase*) 

```
will try to login if not ok then will try to push key with passwd
will push local key to remote, if not specified will list & you can select

if passwd not specified will ask

@param pubkey is the pub key to use (is content of key), if this is specified then keyname
    not used & ssh-agent neither

```

#### get(*executor, usecache=True*) 

```
example:
executor=j.tools.executor.getSSHBased(addr='localhost',
    port=22,login="root",passwd="1234",pushkey="ovh_install")
cuisine=j.tools.cuisine.get(executor)

executor can also be a string like: 192.168.5.5:9022

or if used without executor then will be the local one

```

#### getFromId(*id*) 

#### get_pubkey(*keyname=''*) 

#### reset(*cuisine*) 

```
reset remove the cuisine instance passed in argument from the cache.

```


```
!!!
title = "J Tools Cuisine"
date = "2017-04-08"
tags = []
```

```
!!!
title = "J Tools Cuisine"
date = "2017-04-08"
tags = []
```

```
!!!
title = "J Tools Cuisine"
date = "2017-04-08"
tags = []
```
