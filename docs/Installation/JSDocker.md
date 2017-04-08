# Installing the JumpScale Docker Container
The following instructions will install jumpscale from master. If you want to install from a branch click [here](js_docker_development.md)

The JumpScale Docker container is available on [Docker Hub](https://hub.docker.com/): [jumpscale/ubuntu1604_js_development](https://hub.docker.com/r/jumpscale/ubuntu1604_js_development/).

First make sure you have a Docker machine (host) available, see the Docker documentation for help: https://docs.docker.com/machine/get-started/

In order to list all available machines:

```
docker-machine ls
```

Connect your shell to one of the available Docker machines, for instance in order to connect to **default** (hosted locally on VirtualBox):

```
eval "$(docker-machine env default)"
```

Download the **JumpScale Docker image**:

```
docker pull jumpscale/ubuntu1604_js_development
```

Run a Docker container using the image, and start an interactive session:

```
docker run --rm -t -i --name=js jumpscale/ubuntu1604_js_development
```

In the Docker container let's test the JumpScale interactive shell:

```
export HOME=/root
js
```

An SSH server is installed in the Docker container, but you will have to remap port 22 to some other port on localhost, e.g. 2022.

Create a new one specifying the port mapping:

```
docker run --rm -i -t -p 2022:22 --name="js" jumpscale/ubuntu1604_js_development /sbin/my_init -- bash -l
```

```
!!!
title = "JSDocker"
date = "2017-04-08"
tags = []
```
