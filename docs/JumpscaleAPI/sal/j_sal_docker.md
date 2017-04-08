<!-- toc -->
## j.sal.docker

- /opt/jumpscale8/lib/JumpScale/sal/docker/Docker.py
- Properties
    - base_url
    - logger
    - client

### Methods

#### build(*path, tag, output=True, force*) 

```
path: path of the directory that contains the docker file
tag: tag to give to the image. e.g: 'jumpscale/myimage'
output: print output as it builds

return: strint containing the stdout

```

#### create(*name='', ports='', vols='', volsro='', stdout=True, base='jumpscale/ubuntu1604', nameserver=['8.8.8.8'], replace=True, cpu, mem, ssh=True, myinit=True, sharecode, sshkeyname='', sshpubkey='', setrootrndpasswd=True, rootpasswd='', jumpscalebranch='master', aysfs, detach, privileged, getIfExists=True, weavenet*) 

```
Creates a new container.

@param ports in format as follows  "22:8022 80:8080"  the first arg e.g. 22 is the port in
    the container
@param vols in format as follows "/var/insidemachine:/var/inhost # /var/1:/var/1 # ..."
    '#' is separator
@param sshkeyname : use ssh-agent (can even do remote through ssh -A) and then specify key
    you want to use in docker

```

#### destroyAll(*removeimages*) 

```
Destroy all containers.
@param removeimages bool: to remove all images.

```

#### exists(*name*) 

#### exportRsync(*name, backupname, key='pub'*) 

#### exportTgz(*name, backupname*) 

#### get(*name, die=True*) 

```
Get a container object by name
@param name string: container name

```

#### getImages() 

#### importRsync(*backupname, name, basename='', key='pub'*) 

```
@param basename is the name of a start of a machine locally, will be used as basis and
    then the source will be synced over it

```

#### importTgz(*backupname, name*) 

#### init() 

#### ping() 

#### ps() 

```
return detailed info

```

#### pull(*imagename*) 

```
pull a certain image.
@param imagename string: image

```

#### push(*image, output=True*) 

```
image: str, name of the image
output: print progress as it pushes

```

#### reInstallDocker() 

```
ReInstall docker on your system

```

#### removeDocker() 

#### removeImages(*tag='<none>:<none>'*) 

```
Delete a certain Docker image using tag

```

#### status() 

```
return list docker with some info

@return list of dicts

```

#### weaveInstall(*ufw*) 


```
!!!
title = "J Sal Docker"
date = "2017-04-08"
tags = []
```

```
!!!
title = "J Sal Docker"
date = "2017-04-08"
tags = []
```

```
!!!
title = "J Sal Docker"
date = "2017-04-08"
tags = []
```
