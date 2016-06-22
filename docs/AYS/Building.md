## How to Build an AYS Service (NEEDS TO BE REWORKED)

@todo

Building an AYS means creating the g8fs metadata of the services, if needed actually compiling source code into binary and then pushing the result of the build to an AYS File Store.  

The services are build in a build server where a docker container is spawn every time a new service needs to be build.  
You need to specify in the ``service.hrd`` which docker images you want to use during the build process.

```
build   =
    image: 'jumpscale/ubuntu1510_python',
    repo: 'https://github.com/Jumpscale/docker_ubuntu1510_python.git',
```
``image``: is the name of the docker image to use  
``repo`` is the url of a git repository where a Dockerfile is located. It's used if you want to build the image on the build server itself instead of downloading it from Docker hub.

## Build server infrastructure

Before you start building service you need to make sure you have the correct service instance installed. You need:
- **Build server**: Any 'node' producer
- **ays_stor_client.ssh**: At least one store client cause we need to know where to send the Metadata and binary files after the build.

Here is an example script to deploy a build infrastructure

```
#!/usr/local/bin/jspython

from JumpScale import j

data = {
 'key.name': 'ovh_install',
}
key = j.atyourservice.new(name='sshkey', instance='build', args=data)

buildhostip = "94.23.38.77"
data = {
    'jumpscale.branch': 'ays_unstable',
    'jumpscale.install': False,
    'jumpscale.reset': False,
    'jumpscale.update': False,
    'ssh.port': 22,
    'login': 'root',
    'password': 'supersecret',
    'ip': buildhostip
}
buildhost = j.atyourservice.new(name='node.ssh',instance="master",args=data)


# #INIT THE CACHES & STOR's
data = {
    'read.login': 'read',
    'write.login': 'write',
    'root': "/mnt/data/stor"
}
ays_stor1 = j.atyourservice.new(name='ays_stor.ssh',instance="stor1",parent=buildhost,args=data)

data = {
    'login': 'read',
    'cache': False,
    'ip': buildhostip,
    'ssh.port': 22,
}
storclient1 = j.atyourservice.new(name='ays_stor_client.ssh',instance="storclient",args=data)
storclient1.consume(ays_stor1)

#######################################################

```

### Trigger a build

With the ``ays`` command line:
```bash
ays build -n redis --host 'node.ssh!buildserver' --build --push
```

```
Build:
  --host HOST           key of the build server e.g: 'node.ssh!buildserver'
  --build               enable building of docker image before building the
                        service
  --push                push the docker image after building it.
  --debug               don't clean the docker_build after build. usefull to
                        debug if an error happen durin building

```
Here we trigger the build of the redis service on the build server pointed by ``--host``.  
``--build`` and ``--push`` specify that we want to build the docker image on the build server and then push it on Docker hub. These two flags are optional.

In a Script:
```py
redis = j.atyourservice.getTemplate(name='redis')
redis.build(build_server='node.ssh!buildserver', image_build=False, image_push=False, debug=False)
```

#### Metadata and binary files
AYS FS uses two kind of files to recreate a file system:
- Metadata files
- Binary files

There is one metadata files by AYS templates or instance.
This list contains all the files required by an AYS.

The following is an excerpt of the metadata file of the ```jumpscale__base``` service.
```
/opt/jumpscale8/bin/jsnet|8a3e5e03a10ecc3601a1f14fbc371019|4857
/opt/jumpscale8/bin/jsnode|793384b5bde2901461606146adbed382|5088
/opt/jumpscale8/bin/jsportalclient|76f87551c60336da45c379f38625144b|1553
/opt/jumpscale8/bin/jsprocess_monitor|127546640e1f98c3d35bbd03153a1e17|248
/opt/jumpscale8/bin/jsprocess_startAllReset|e839ddaa3d391c9d099cb513d538c62b|184
/opt/jumpscale8/bin/jsprocess|397f026a662f1316421b78e8c6c5b5f7|4506

```

The format is   ```/$path/$name|$hash|$size```

The hash is an md5 hash of the content of the file. It's used to link the metadata with it's binary content. It also allow us to creates dedupe namespace where the binary content is never duplicated.

The binary content is stores in a directory structure with 3 levels.
First two level are the first and second character of the hash of the file and the last level contain the actual binary file named with the full md5 hash.
```
a
├── 0
│   ├── a001d62d00fbeb0f1ef4e77e5d8c5e3d
│   ├── a0237c980711ed468f39b5c178ccf875
│   ├── a03e021c3623542e16c47df9799ff8a5
│   ├── a043b3974df8701a8d3cf686690795f8
├── 1
│   ├── a12abc97671995529a05ae1fa73120c9
│   ├── a134ce45aa49528684f9bbc6c2e8042c
│   ├── a139377c7036f280449d8a6746501c18
│   ├── a13bc16af414cc4bdfb9d554c50842d9
...
```

## Build Method
Every service need to have a build method in their actions_mgmt file.
By default the build method just walk over the 'git.export' entries from the service HRD, download the files locally then create the metadata files and put the binary in the correct directory structure

This is the code of the default build method:
```py
folders = serviceObj.installRecipe()

for src, dest in folders:
    serviceObj.upload2AYSfs(dest)
```

Of course if your service requires more action you need to overwrite the default method and write the implementation yourself.
