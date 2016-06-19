## LXC

```py
j.sal.lxc
```

Helps you with your LXC containers.

### Usage

* List all containers

```py
j.sal.lxc.list()
```

* Creating a container

```py
j.sal.lxc.create(self,name="",stdout=True,base="base",start=False,nameserver="8.8.8.8",replace=True):
```

* Start a container

```py
j.sal.lxc.start(name,stdout=True,test=True)
```

* Stopping a container

```py
j.sal.lxc.stop(name)
```

* Destroy a container

```py
j.sal.lxc.destroy(name)
```

* Destroy all containers
```py
j.sal.lxc.destroyAll()
```

* Remove redundant files (.bak, .pyc)

```py
j.sal.lxc.removeRedundantFiles(name)
```

* Export a container as TGZ tarball

```py
j.sal.lxc.exportTgz(name,backupname)
```

* Import a container from a TGZ tarball

```py
j.sal.lxc.importTgz(backupname,name)
```

* Export a container via rsync

```py
j.sal.lxc.exportRsync(name,backupname,key="pub")
```

* Import a container from rsync

```py
j.sal.lxc.importRsync(backupname,name,basename="",key="pub")
```

* Get process list

```py
j.sal.lxc.getProcessList(name, stdout=True)
```

* Get PID 
```py
j.sal.lxc.getPid(name,fail=True)
```

* Set hostname

```py
j.sal.lxc.setHostName(name)
```

* Getting the Ip
```py
j.sal.lxc.getIP()
```

* Setting up a network

```py
j.sal.lxc.networkSet(self, machinename,netname="pub0",pubips=[],bridge="public",gateway=None)
```

* Pushing SSH key 

```py
j.sal.lxc.pushSSHKey(name)
```