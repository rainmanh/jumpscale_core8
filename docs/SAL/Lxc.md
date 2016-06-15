# LXC
```
j.sal.lxc
```
Helps you with your LXC containers.

## Usage
* Listing all containers
```
j.sal.lxc.list()
```
* Creating a container
```
j.sal.lxc.create(self,name="",stdout=True,base="base",start=False,nameserver="8.8.8.8",replace=True):
```
* Starting a container
```
j.sal.lxc.start(name,stdout=True,test=True)
```
* Stopping a container
```
j.sal.lxc.stop(name)
```

* Destroy a container
```
j.sal.lxc.destroy(name)
```
* Destroy all containers
```
j.sal.lxc.destroyAll()
```

* Remove redundant files (.bak, .pyc)
```
j.sal.lxc.removeRedundantFiles(name)
```
* Export a container as TGZ tarball
```
j.sal.lxc.exportTgz(name,backupname)
```
* Import a container from a TGZ tarball
```
j.sal.lxc.importTgz(backupname,name)
```
* Export a container via rsync
```
j.sal.lxc.exportRsync(name,backupname,key="pub")
```
* Import a container from rsync
```
j.sal.lxc.importRsync(backupname,name,basename="",key="pub")
```

execute

* Get process list
```
j.sal.lxc.getProcessList(name, stdout=True)
```
* Get PID 
```
j.sal.lxc.getPid(name,fail=True)
```

* Set hostname
```
j.sal.lxc.setHostName(name)
```
* Getting the Ip
```
j.sal.lxc.getIP()
```

* Setting up a network
```
j.sal.lxc.networkSet(self, machinename,netname="pub0",pubips=[],bridge="public",gateway=None)
```
* Pushing SSH key 
```
j.sal.lxc.pushSSHKey(name)

```


