## example how to use ays to automate vmachines in docker


The following example will:

- create docker node with ays called master
- create docker node with ays called client
- install jumpscale in both dockers
- install jumpscale AgentController8 in master
- install jumpscale agent8 in client

requirements

- all docker based
- start from ubuntu 15.04 64 bit, use jsdocker way of working (see docs)

## todo complete

```
datacenter__ovh_germany1:
  location:
    - '...'
  description:
    - '...'

rack__ovh_1:
  location:
    - 'here'
  datacenter: 'ovh_germany1'

sshkey__ovh_install:
  key.path: '/root/.ssh/ovh_rsa'

#no need to specify a sshkey, because there is only 1 will use that one
node.physical__ovh4:
  rack: 'ovh_1'
  type: 'develop'

os.ssh.ubuntu__ovh4:
  ssh.addr: '1.1.1.1'
  ssh.port: 22
  ssh.key: 'ovh_install' 
  node: 'ovh4'
  aysfs: False

node.docker__master:
  ssh.key: 'ovh_install' 
  image: 'ubuntu 15.04'
  ports:
    - 80
  os: 'ovh4'

os.ssh.ubuntu__docker_master:
  ssh.key: 'ovh_install' 
  node: 'master'
  g8os_fs: False

node.docker__client:
  ssh.key: 'ovh_install' 
  image: 'ubuntu 15.04'
  ports:
    - 80
  os: 'ovh4'

os.ssh.ubuntu__docker_client:
  ssh.key: 'ovh_install' 
  node: 'client'
  g8os_fs: False
  agent: true

```
