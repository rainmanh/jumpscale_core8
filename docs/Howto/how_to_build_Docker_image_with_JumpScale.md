# Building your own Docker image

We made this task very easy for you.

You just need to get the [dockers](https://github.com/Jumpscale/dockers) repository and follow the build instructions below.

Also you can customize your image and build it the same way as the examples in the repo.

## Pre-requirements

- Make sure you have the latest version of docker installed
- GNU make

## Building the base images

To start building the base images first clone and prepare the repository:

```bash
git clone https://github.com/Jumpscale/dockers.git
cd dockers
git submodule init
```

> Note: The `git submodule init` is only required once the first time you clone the repository. No need to rerun this command for the future builds.

```bash
cd ./images
ls -l
```

```raw
total 0
drwxr-xr-x 1 azmy azmy 54 Sep  8 15:59 AgentController8
drwxr-xr-x 1 azmy azmy 54 Sep  8 15:29 ubuntu15.04
drwxr-xr-x 1 azmy azmy 54 Sep  8 13:19 ubuntu15.10
```

We have 2 base images:

- ubuntu 15.04
- ubuntu 15.10

Each has the following pre-configuration:

- Working SSH
- Root password set to `js007`
- Latest JumpScale8 (at the time of the build) pre-installed
- Auto starts all installed `@ys` services
- System Redis

We also have the `AgentController8` as an example of a custom image that uses `ubuntu15.04` image to pre-install some services. If you need to build a custom image that pre-installs your apps and services you can use this one as a guide. Note that this image won't build unless `ubuntu15.04` was build already.

Now to build the base images do the following:

```bash
cd dockers/images/ubuntu15.04
make
```

Make will take care of everything and will take sometime, but when it's done you will have the `jumpscale/ubuntu15.04` image ready.

```bash
docker images
```

Will have this in its output

```raw
REPOSITORY                   TAG                 IMAGE ID            CREATED             VIRTUAL SIZE
jumpscale/ubuntu             15.04               6cc68f352eb8        20 hours ago        630.4 MB
```

## Running the image

```bash
docker run --rm -ti --name test jumpscale/ubuntu:15.04
```

> You can use -d instead to run in the background, but the `-ti` option is good for testing so you can see the boot sequence

```bash
docker inspect test | grep IPAddress
# "IPAddress": "172.17.0.1",
```

> IPAddress might be different in your case.

```bash
ssh root@172.17.0.1
# Password: js007
```

```bash
test:/# ays status
DOMAIN          NAME                 Instance   Prio Status   Ports
======================================================================

jumpscale       redis                main          1 RUNNING  9999
```

> Installed AYS services already running.

## To run the image with jsdocker

JumpScale comes with a command line tool that abstract working with dockers. To run a new jsdocker image simply do the following:

```bash
jsdocker new -n test -b jumpscale/AgentController8:15.04
```

This will output something like

```raw
create:test
SSH PORT WILL BE ON:9022
MAP:
 /var/jumpscale       /var/docker/test
 /tmp/dockertmp/test  /tmp
install docker with name 'jumpscale/AgentController8:15.04'
test docker internal port:22 on ext port:9022
connect ssh2
[localhost:9022] Login password for 'root': js007
```

Note that `jsdocker` will auto map container ssh port to a free local port (9022 in this example) so to connect to the new running container simply do:

```bash
ssh -p 9022 root@localhost
```
