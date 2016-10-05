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
Create new container
@param name if "" then will be an incremental nr
@param start bool: start the container after creation.

```

#### destroy(*name*) 

```
Destroy container by name
@param name str: name

```

#### destroyAll() 

```
Destroy all running containers.

```

#### execute(*command*) 

```
Execute command.

@param command str: command to run

```

#### exportRsync(*name, backupname, key='pub'*) 

#### exportTgz(*name, backupname*) 

```
Export a container to a tarball
@param backupname str: backupname
@param name str: container name.

```

#### getConfig(*name*) 

#### getIp(*name, fail=True*) 

```
Get IP of container
@param name str: containername.

```

#### getPid(*name, fail=True*) 

#### getProcessList(*name, stdout=True*) 

```
Get process list on a container.
@return [["$name",$pid,$mem,$parent],....,[$mem,$cpu]]
last one is sum of mem & cpu

```

#### importRsync(*backupname, name, basename='', key='pub'*) 

```
@param basename is the name of a start of a machine locally, will be used as basis and
    then the source will be synced over it

```

#### importTgz(*backupname, name*) 

```
Import a container from a tarball
@param backupname str: backupname
@param name str: container name.

```

#### list() 

```
names of running & stopped machines
@return (running,stopped)

```

#### networkSet(*machinename, netname='pub0', pubips, bridge='public', gateway*) 

#### networkSetPrivateVXLan(*name, vxlanid, ipaddresses*) 

#### pushSSHKey(*name*) 

```
Push sshkey
@param name str: keyname

```

#### removeRedundantFiles(*name*) 

#### setHostName(*name*) 

```
Set hostname on the container
@param name: new hostname

```

#### start(*name, stdout=True, test=True*) 

```
Start container
@param name str: container name.

```

#### stop(*name*) 

```
Stop a container by name
@param name str: container name.

```

