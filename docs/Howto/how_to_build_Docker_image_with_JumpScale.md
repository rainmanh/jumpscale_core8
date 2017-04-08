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
total 12                                                                                                                                                                                                   
drwxr-xr-x  3 khaled khaled 4096 18 16:17 armhf                                                                                                                                                        
drwxrwxr-x  5 khaled khaled 4096 31 15:43 test                                                                                                                                                         
drwxr-xr-x 20 khaled khaled 4096 أ31 15:43 x86_64
```

We have 3 directories that contains multiple images:

- armhf
- test
- x86_64

Each has the following pre-configuration:

- Python3
- Working SSH
- Root password set to `gig1234`

We also have the `AgentController8` as an example of a custom image that uses `ubuntu15.04` image to pre-install some services. If you need to build a custom image that pre-installs your apps and services you can use this one as a guide. Note that this image won't build unless `ubuntu15.04` was build already.

Now to build the base images do the following:

```bash
cd dockers/js8/x86_64/31_ubuntu1604_js8/
docker build -t jumpscale/ubuntu1604 --no-cache .
```


Will have this in its output

```raw
REPOSITORY                   TAG                 IMAGE ID            CREATED             VIRTUAL SIZE
jumpscale/ubuntu1604           latest              54236fee1523        2 minutes ago       357 MB
```

## Running the image

```bash
docker run --rm -ti --name test jumpscale/ubuntu1604
```

> You can use -d instead to run in the background, but the `-ti` option is good for testing so you can see the boot sequence

```bash
docker inspect test | grep IPAddress
# "IPAddress": "172.17.0.1",
```

> IPAddress might be different in your case.

```bash
ssh root@172.17.0.1
# Password: gig1234
```

## To run the image with jsdocker

JumpScale comes with a command line tool that abstract working with dockers. To run a new jsdocker image simply do the following:

```bash
jsdocker create -i jumpscale/ubuntu1604 -n test
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
[localhost:9022] Login password for 'root': gig1234
```

Note that `jsdocker` will auto map container ssh port to a free local port (9022 in this example) so to connect to the new running container simply do:

```bash
ssh -p 9022 root@localhost
```

```
!!!
title = "How To Build Docker Image With JumpScale"
date = "2017-04-08"
tags = ["howto"]
```
