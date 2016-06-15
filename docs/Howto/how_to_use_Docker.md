# How to use Docker

Make sure you have the latest JumpScale installed.

## Install Docker
```bash
ays init -n docker
ays apply
```

## Use Docker
We already have a base Docker image ready to use `despiegk/mc`. You also can [building your own Docker image](how_to_build_Docker_image_with_JumpScale.md).

```bash
docker pull despiegk/mc

#standard /tmp/docker/tmp will be mapped & /code to be same in docker
#std port 9022 will be mapped to ssh (if only 1 docker)
#-j will also install jumpscale (make sure you have it installed locally)
jsdocker new -n test -j

#more detailed example
#sjdocker new -n kds --ports "22:9022 7766:9766" --vols "/mydata:/mydata" --cpu 100

#to login
ssh localhost -p 9022

#now you can install whatever apps using JumpScale
(test)# apt-get update
```

Now you can use `@ys` to install JumpScale packages.

```bash
ays init -n redis
ays apply
```

## Commit your changes
When you setup your apps, and you are happy with your pre-set Docker container, you can commit your changes for later use or distribution by doing the following:

```bash
#first get a docker running e.g. 
jsdocker new -n test -j

#1- SSH to running container
#2- Install apps you want on that instance

#On host, show which docker running
docker ps

#now we can push docker image to repo
docker commit test myimage
# If you have dockerhub account, you can push your image to dockerhub

#to run the newly created docker image do the following
docker run -d -p 9022:22 -v /opt/code/:/opt/code myimage /sbin/my_init
```

## Use Docker extension to start Docker containers
Here is an example script on how to use `JumpScale` Docker extension to manage your docker machines.

[do.py](https://github.com/Jumpscale/play7/blob/master/docker_jumpscale_development/do.py)

```python
from JumpScale import j


def docker_create_machine(name, reinstall=False, image='despiegk/mc'):
    docker = j.atyourservice.findTemplates(name='node.docker')[0]
    ports = "8086:8086 8083:8083 28017:28017 27017:27017 5544:5544 82:82"
    vols = "/opt/jumpscale/var/influxdb:/var/mydocker/influxdb # /opt/jumpscale/var/mongodb:/var/mydocker/mongodb"
    args = {
        'instance.param.name': name,
        'instance.param.image': image,
        'instance.param.portsforwards': ports,
        'instance.param.volumes': vols,
    }

    docker.install(name, reinstall=reinstall, args=args)

###################################################################################
if __name__ == '__main__':
    name = 'master'
    docker_create_machine(name=name, reinstall=True)
    instance = j.atyourservice.findServices(name='node.docker', instance=name)[0]

    portal = j.atyourservice.findTemplates(name='singlenode_portal')[0]
    portal.install(parent=instance)

    info = j.tools.docker.inspect(name)

    port = info['NetworkSettings']['Ports']['22/tcp'][0]['HostPort']
    print "SSH port of docker is: %s" % port

```