# LXC

```python
j.sal.lxc
```

Helps you with your LXC containers.

## Usage

- List all containers

```python
j.sal.lxc.list()
```

- Creating a container

```python
j.sal.lxc.create(self,name="",stdout=True,base="base",start=False,nameserver="8.8.8.8",replace=True):
```

- Start a container

```python
j.sal.lxc.start(name,stdout=True,test=True)
```

- Stopping a container

```python
j.sal.lxc.stop(name)
```

- Destroy a container

```python
j.sal.lxc.destroy(name)
```

- Destroy all containers

  ```python
  j.sal.lxc.destroyAll()
  ```

- Remove redundant files (.bak, .pyc)

```python
j.sal.lxc.removeRedundantFiles(name)
```

- Export a container as TGZ tarball

```python
j.sal.lxc.exportTgz(name,backupname)
```

- Import a container from a TGZ tarball

```python
j.sal.lxc.importTgz(backupname,name)
```

- Export a container via rsync

```python
j.sal.lxc.exportRsync(name,backupname,key="pub")
```

- Import a container from rsync

```python
j.sal.lxc.importRsync(backupname,name,basename="",key="pub")
```

- Get process list

```python
j.sal.lxc.getProcessList(name, stdout=True)
```

- Get PID

  ```python
  j.sal.lxc.getPid(name,fail=True)
  ```

- Set hostname

```python
j.sal.lxc.setHostName(name)
```

- Getting the Ip

  ```python
  j.sal.lxc.getIP()
  ```

- Setting up a network

```python
j.sal.lxc.networkSet(self, machinename,netname="pub0",pubips=[],bridge="public",gateway=None)
```

- Pushing SSH key

```python
j.sal.lxc.pushSSHKey(name)
```
