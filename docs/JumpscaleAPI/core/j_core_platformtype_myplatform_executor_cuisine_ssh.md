<!-- toc -->
## j.core.platformtype.myplatform.executor.cuisine.ssh

- /opt/jumpscale8/lib/JumpScale/tools/cuisine/CuisineSSH.py

### Methods

#### authorize(*user, key*) 

```
Adds the given key to the '.ssh/authorized_keys' for the given
user.

```

#### enableAccess(*keys, backdoorpasswd, backdoorlogin='backdoor', user='root'*) 

```
make sure we can access the environment
keys are a list of ssh pub keys

```

#### keygen(*user='root', keytype='rsa', name='default'*) 

```
Generates a pair of ssh keys in the user's home .ssh directory.

```

#### scan(*range, ips, port=22*) 

```
@param range in format 192.168.0.0/24
if range not specified then will take all ranges of local ip addresses (nics)

```

#### sshagent_add(*path, removeFirst=True*) 

```
@path is path to private key

```

#### sshagent_remove(*path*) 

```
@path is path to private key

```

#### test_login(*passwd, port=22, range, onlyplatform='arch'*) 

#### test_login_pushkey(*passwd, keyname, port=22, range, changepasswdto='', onlyplatform='arch'*) 

#### unauthorize(*user, key*) 

```
Removes the given key to the remote '.ssh/authorized_keys' for the given
user.

```

#### unauthorizeAll() 


```
!!!
title = "J Core Platformtype Myplatform Executor Cuisine Ssh"
date = "2017-04-08"
tags = []
```

```
!!!
title = "J Core Platformtype Myplatform Executor Cuisine Ssh"
date = "2017-04-08"
tags = []
```

```
!!!
title = "J Core Platformtype Myplatform Executor Cuisine Ssh"
date = "2017-04-08"
tags = []
```
