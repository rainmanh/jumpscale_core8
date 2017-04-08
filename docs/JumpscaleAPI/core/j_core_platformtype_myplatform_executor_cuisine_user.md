<!-- toc -->
## j.core.platformtype.myplatform.executor.cuisine.user

- /opt/jumpscale8/lib/JumpScale/tools/cuisine/CuisineUser.py

### Methods

#### check(*name, uid, need_passwd=True*) 

```
Checks if there is a user defined with the given name,
returning its information as a
'\{"name":<str>,"uid":<str>,"gid":<str>,"home":<str>,"shell":<str>\}'
or 'None' if the user does not exists.
need_passwd (Boolean) indicates if password to be included in result or not.
    If set to True it parses 'getent shadow' and needs self._cuisine.core.sudo access

```

#### create(*name, passwd, home, uid, gid, shell, uid_min, uid_max, encrypted_passwd=True, fullname, createhome=True*) 

```
Creates the user with the given name, optionally giving a
specific password/home/uid/gid/shell.

```

#### ensure(*name, passwd, home, uid, gid, shell, fullname, encrypted_passwd=True, group*) 

```
Ensures that the given users exists, optionally updating their
passwd/home/uid/gid/shell.

```

#### list() 

#### passwd(*name, passwd, encrypted_passwd*) 

```
Sets the given user password.

```

#### remove(*name, rmhome*) 

```
Removes the user with the given name, optionally
removing the home directory and mail spool.

```


```
!!!
title = "J Core Platformtype Myplatform Executor Cuisine User"
date = "2017-04-08"
tags = []
```

```
!!!
title = "J Core Platformtype Myplatform Executor Cuisine User"
date = "2017-04-08"
tags = []
```

```
!!!
title = "J Core Platformtype Myplatform Executor Cuisine User"
date = "2017-04-08"
tags = []
```
