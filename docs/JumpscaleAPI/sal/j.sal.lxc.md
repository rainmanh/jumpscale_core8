<!-- toc -->
## j.sal.lxc

- /opt/jumpscale8/lib/JumpScale/sal/lxc/Lxc.py

### Methods

#### btrfsSubvolCopy(*nameFrom, NameDest*) 

#### btrfsSubvolDelete(*name*) 

#### btrfsSubvolExists(*name*) 

#### btrfsSubvolList() 

#### btrfsSubvolNew(*name*) 

#### create(*name='', stdout=True, base='base', start, nameserver='8.8.8.8', replace=True*) 

```
@param name if "" then will be an incremental nr

```

#### destroy(*name*) 

#### destroyAll() 

#### execute(*command*) 

#### exportRsync(*name, backupname, key='pub'*) 

#### exportTgz(*name, backupname*) 

#### getConfig(*name*) 

#### getIp(*name, fail=True*) 

#### getPid(*name, fail=True*) 

#### getProcessList(*name, stdout=True*) 

```
@return [["$name",$pid,$mem,$parent],....,[$mem,$cpu]]
last one is sum of mem & cpu

```

#### importRsync(*backupname, name, basename='', key='pub'*) 

```
@param basename is the name of a start of a machine locally, will be used as basis and
    then the source will be synced over it

```

#### importTgz(*backupname, name*) 

#### list() 

```
names of running & stopped machines
@return (running,stopped)

```

#### networkSet(*machinename, netname='pub0', pubips, bridge='public', gateway*) 

#### networkSetPrivateVXLan(*name, vxlanid, ipaddresses*) 

#### pushSSHKey(*name*) 

#### removeRedundantFiles(*name*) 

#### setHostName(*name*) 

#### start(*name, stdout=True, test=True*) 

#### stop(*name*) 

