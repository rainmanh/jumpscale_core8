# Installing Docker and Caddy using AYS
First we should define our Blueprint like this

## blueprints/docker.yaml
```
g8client__gig:
  g8.url: 'gig.demo.greenitglobe.com'
  g8.login: 'username'
  g8.password: 'password'
  g8.account: 'operations'

vdcfarm__vdcfarm1:

vdc__vdc4moscow:
  vdcfarm: 'vdcfarm1'
  g8.client.name: 'gig'
  g8.location: 'be-scale-2'

node.ovc__vm4docker:
  os.image: 'ubuntu 14.04 x64'
  vdc: 'vdc4moscow'
  ports: '80:8888'

os.ssh.ubuntu__vm4docker:
  node: 'vm4docker'

app_docker__docker:
  os: vm4docker

node.docker__docker:
  image: 'jumpscale/demomoscow'
  restart: true
  os: 'vm4docker'
  docker: docker
  ports:
    - '8888:8888'
dns_client__dns:

webserver.caddy__caddy:
  os: 'vm4docker'
  domain: 'gigdomain'
  dns_client: 'dns
```

1. In the blueprint we define which services we will use:
like at first line
```
g8client__gig
```
The first part is the service role(g8clinet) and the second part is the service instance (gig)
those two parts are separated with two underscore(`__`)
so the definition should be $role__$instance

2. Then we pass each service a group of parameters that this service use to complete it's Work like:
`g8.url, g8.logine, g8.password, g8.account`
with a quick look at the schema of the g8client we can easly figure out all the required parameters

3. In the `vdc__vdc4moscow` we used the g8client that we created at the first step because in the schema of the `vdc` we will find that it uses (consumes) `g8client`
##vdc/schema.hrd
```
...
g8.client.name = type:str consume:'g8client' auto                                        ...            
```
## g8clinet/schema.hrd
```
g8.url = type:str default:'http://www.mothership1.com'
g8.login = type:str default:'???'
g8.password= type:str default:'???'
g8.account= type:str default:''
```

after defining all required services we should have this directory structure
```
.
├── blueprints
│   └── docker.yaml
├── .ays
```

then from our root dir we should execute
```
ays blueprint
```
then
```
ays install
```

after executing these commands we should have this structure

```
.
├── blueprints
│   └── dockercaddy
├── recipes
│   ├── app_docker
│   ├── dns_client
│   ├── g8client
│   ├── node.docker
│   ├── node.ovc
│   ├── os.ssh.ubuntu
│   ├── sshkey
│   ├── vdc
│   ├── vdcfarm
│   └── webserver.caddy
└── services
    ├── app_docker!docker
    ├── dns_client!dns
    ├── g8client!gig
    └── vdcfarm!vdcfarm1

```

```
!!!
title = "Install Docker And Caddy"
date = "2017-04-08"
tags = []
```
