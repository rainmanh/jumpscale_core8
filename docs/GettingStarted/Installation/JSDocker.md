# Working with Docker

## Without having JumpScale pre-installed

```
docker pull jumpscale/ubuntu1604_golang
#next will run & login into the docker
docker run --rm -t -i  --name=js jumpscale/ubuntu1604_golang
```

In the Docker container:
```
export HOME=/root
js
```

You will now see a shell for JumpScale.

An SSH server is installed in the Docker container, but you will have to remap port 22 to some other port on localhost, e.g. 2022.

Here's how:
```
docker rm -f js
docker run --rm -i -t -p 2022:22 --name="js" jumpscale/ubuntu1604_golang /sbin/my_init -- bash -l
```

## With JumpScale already installed (recommended way)

### Install the Docker container with Cuisine

From your local machine with JumpScale pre-installed we will connect over SSH to a remote Ubuntu 16.04 server (here called myhost), and install Docker host and JumpScale on it.

First op the shell:
```
js
```

Using the interactive shell we establish a connection to the remote server:

```
c = j.tools.cuisine.get("myhost") #can also use ipaddress
```

Alternatively use following command if SSH is listening on another port:

```
c = j.tools.cuisine.get("192.168.4.4:2200")`
```

For the next step make sure the your SSK public key is know on the remote server and that your private key is loaded in ssh-agent.

Now let's install Docker on the remote server:
```
c.docker.install()
```

In case JumpScale is not installed yet installed on the remote server, install it using following commands:
```
c.install.jumpscale8()
```

The above will install JumpScale 8 using our virtual filesystem layer.

Now login to the Ubuntu server and use the following commands to start a new Docker container:

```
jsdocker create -n kds -i jumpscale/ubuntu1604_golang -k mykey
```

With the above command port 9022 will be mapped by default to the SSH port of the Docker container (if only 1 Docker container). With the **-k** option you specify the SSH key to be used (name as loaded in ssh-agent). If no key is specified, a local one will be created.

Alternatively you can do more sophisticated things:
```
jsdocker new -n kds --ports "22:9022 7766:9766" --vols "/mydata:/mydata" --cpu 100
```

To list the Dockers containers:
```
jsdocker list

 Name                 Imange                    host                 ssh port   status
 kds                  jumpscale/ubuntu1604      localhost            9023       Up 27 seconds
 build                jumpscale/ubuntu1604      localhost            9022       Up 20 minutes
 owncloudproxy        owncloudproxy             localhost                       Up 24 hours
 owncloud             owncloud:live             localhost                       Up 24 hours
```

To login:
```
ssh localhost -p 9022
```

## Build Docker images

- Checkout repo: <https://github.com/Jumpscale/dockers>
- Go to <https://github.com/Jumpscale/dockers/tree/master/js8/x86_64> and use the `buildall` command

```
Usage: buildall.py [OPTIONS]

  builds dockers with jumpscale components if not options given will ask
  interactively

  to use it remotely, docker & jumpscale needs to be pre-installed

Options:
  -h, --host TEXT      address:port of the docker host to use
  --debug / --nodebug  enable or disable debug (default: True)
  --push / --nopush    push images to docker hub afrer building
                       (default:False)
  -i, --image TEXT     specify which image to build e.g. 2_ubuntu1604, if not
                       specified then will ask, if * then all.
  --help               Show this message and exit.
```

### Example using a remote machine to build

For the example below:

- Remote machine name is `ovh4`
- Docker and JumpScale need to be pre-installed
- When selecting e.g. 2 a basic Ubuntu 16.04 will be build
- With `--push` option the Docker images will be pushed to Docker Hub, which will only work if you have rights

```
bash-3.2$ python3 buildall.py --host ovh4:22 --push
[Fri24 11:26] - ...ib/JumpScale/clients/ssh/SSHClient.py:160  - INFO     - Test connection to ovh4:22
[Fri24 11:26] - ...ib/JumpScale/sal/nettools/NetTools.py:60   - DEBUG    - test tcp connection to 'ovh4' on port 22
[Fri24 11:26] - ...ib/JumpScale/clients/ssh/SSHClient.py:126  - INFO     - ssh new client to root@ovh4:22

Please select dockers you want to build & push.
   1: g8os
   2: ubuntu1604
   3: ubuntu1604_python3
   4: ubuntu1604_js8
   5: ubuntu1604_golang
   6: sandbox
   7: pxeboot

   Select Nr, use comma separation if more e.g. "1,4", * is all, 0 is None:
```
