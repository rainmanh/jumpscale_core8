# Docker
This sal helps you to manipulate docker containers and images. 
```
j.sal.docker
```
## Usage
* Creation of a docker container
```
j.sal.docker.create(name="", ports="", vols="", volsro="", stdout=True, base="jumpscale/ubuntu1504", nameserver=["8.8.8.8"], replace=True, cpu=None, mem=0, jumpscale=False, ssh=True, myinit=True, sharecode=False,sshkeyname="",sshpubkey="", setrootrndpasswd=True,rootpasswd="",jumpscalebranch="master")
```
* Connect to a remote TCP host.
```
j.sal.docker.connectRemoteTCP(address,port)
```
* Check if a container exists.
```
j.sal.docker.exists(name)
```
* Searches for a container with a specific name and returns it as a `Container` object
```
j.sal.docker.get(name)
```

* List all containers and their names.
```
j.sal.docker.containers()
j.sal.docker.containerNames()
```
* List all running containers and their names.
```
j.sal.docker.containersRunning()
j.sal.docker.containerNamesRunning()
```
* Pull a docker image from connected host.
```
j.sal.docker.pull(imagename)
```
* List all available docker images.
```
j.sal.docker.getImages()
```
* Delete a certain docker image `ubuntu:xenial` for instance.
```
j.sal.docker.removeImages(tag)
```
* Destroy all docker containers.
```
j.sal.docker.destroyContainers()
```
* Reset docker with all it's containers.
```
j.sal.docker.resetDocker()
```
* Push a docker image to connected host.
```
j.sal.docker.push(imagename)
```
* Get summarized and detailed information about a certain docker container.
```
j.sal.docker.status()
j.sal.docker.ps()
```

* Export as TGZ tarball
```
j.sal.docker.exportTGZ(name,backupname)
```
* Import from a tarball
```
j.sal.docker.importTgz(self,backupname,name)
```

* Export RSYNC
```
j.sal.docker.exportRsync(name,backupname,key="pub")
```
* Import RSync
```
j.sal.docker.importRsync(self,backupname,name,basename="",key="pub")

```
* Building a dockerfile
```
j.sal.docker.build(path, tag, output=True)
```


