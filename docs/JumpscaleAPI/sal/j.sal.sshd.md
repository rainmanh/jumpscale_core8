<!-- toc -->
## j.sal.sshd

- /opt/jumpscale8/lib/JumpScale/sal/sshd/SSHD.py

### Methods

#### addKey(*key*) 

```
Add pubkey to authorized_keys

```

#### commit() 

```
Apply all pending changes to authorized_keys

```

#### deleteKey(*key*) 

```
Delete pubkey from authorized_keys

```

#### disableNonKeyAccess() 

```
Disable passowrd login to server. This action doens't require
calling to commit and applies immediately. So if you added your key
make sure to commit it before you call this method.

```

#### erase() 

```
Erase all keys from authorized_keys

```

