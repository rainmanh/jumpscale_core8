# Installing a Docker Container with JumpScale Pre-installed


Source: jumpscale/ubuntu1604_js_development

...

Review/Rework te below:

```
docker pull jumpscale/ubuntu1604_golang
#next will run & login into the docker
docker run --rm -t -i  --name=js jumpscale/ubuntu1604_golang
```

In the Docker container let's test the JumpScale interactive shell:
```
export HOME=/root
js
```

An SSH server is installed in the Docker container, but you will have to remap port 22 to some other port on localhost, e.g. 2022.

Here's how:
```
docker rm -f js
docker run --rm -i -t -p 2022:22 --name="js" jumpscale/ubuntu1604_golang /sbin/my_init -- bash -l
```
