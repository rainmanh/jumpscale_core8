# Installing the JumpScale Docker Container

The JumpScale Docker container is available on [Docker Hub](https://hub.docker.com/): [jumpscale/ubuntu1604_js_development](https://hub.docker.com/r/jumpscale/ubuntu1604_js_development/).


In order to create a Docker container and start an interactive session in the container:

```
docker pull jumpscale/ubuntu1604_js_development
docker run --rm -t -i  --name=js jumpscale/ubuntu1604_golang
```

In the Docker container let's test the JumpScale interactive shell:
```
export HOME=/root
js
```

An SSH server is installed in the Docker container, but you will have to remap port 22 to some other port on localhost, e.g. 2022.

So first remove the existing container, and create a new one specifying the port mapping:
```
docker rm -f js
docker run --rm -i -t -p 2022:22 --name="js" jumpscale/ubuntu1604_golang /sbin/my_init -- bash -l
```
