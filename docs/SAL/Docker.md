# Docker

This SAL helps you to manipulate docker containers and images.

```python
j.sal.docker
```

## Usage

- Create of a Docker container

```python
j.sal.docker.create(name="", ports="", vols="", volsro="", stdout=True, base="jumpscale/ubuntu1504", nameserver=["8.8.8.8"], replace=True, cpu=None, mem=0, jumpscale=False, ssh=True, myinit=True, sharecode=False,sshkeyname="",sshpubkey="", setrootrndpasswd=True,rootpasswd="",jumpscalebranch="master")
```

- Connect to a remote TCP host

```python
j.sal.docker.connectRemoteTCP(address,port)
```

- Check if a container exists

```python
j.sal.docker.exists(name)
```

- Searche for a container with a specific name and returned as a `Container` object

```python
j.sal.docker.get(name)
```

- List all containers and their names

```python
j.sal.docker.containers()
j.sal.docker.containerNames()
```

- List all running containers and their names

```python
j.sal.docker.containersRunning()
j.sal.docker.containerNamesRunning()
```

- Pull a Docker image from connected host

```python
j.sal.docker.pull(imagename)
```

- List all available Docker images

```python
j.sal.docker.getImages()
```

- Delete a certain Docker image:

```python
j.sal.docker.removeImages(tag)
```

- Destroy all Docker containers

```python
j.sal.docker.destroyContainers()
```

- Reset docker with all it's containers

```python
j.sal.docker.resetDocker()
```

- Push a Docker image to connected host

```python
j.sal.docker.push(imagename)
```

- Get summarized and detailed information about a certain Docker container

```python
j.sal.docker.status()
j.sal.docker.ps()
```

- Export as TGZ tarball

```python
j.sal.docker.exportTGZ(name,backupname)
```

- Import from a tarball

```python
j.sal.docker.importTgz(self,backupname,name)
```

- Export RSYNC

```python
j.sal.docker.exportRsync(name,backupname,key="pub")
```

- Import RSync

```python
j.sal.docker.importRsync(self,backupname,name,basename="",key="pub")
```

- Building a dockerfile

```python
j.sal.docker.build(path, tag, output=True)
```
