## example how to use ays to automate creation of 2 machines in openvcloud or mothership1

following jumpscript will

- create ms1 node
- inside ms1 node: (see DockerExample.md)
    - create docker node with ays called master
    - create docker node with ays called client
    - install jumpscale in both dockers
    - install jumpscale AgentController8 in master
    - install jumpscale agent2 in client
    - do a test where a command gets executed on client from master & return works

remarks

- all docker based
- start from ubuntu 15.04 or 14.04 64 bit, use jsdocker way of working (see docs)
- start from env arguments for ms1 passwd, rest in ays instance ovc_client
- if passwd env arguments not filled in dynamically ask for it


ays examples are stored in


#@todo complete

```

g8_client__main:
    g8.account: {g8.account}
    g8.url: {g8.url}
    g8.password: {g8.password}

sshkey__main:

vdcfarm__main:

vdc__spacename:
    vdcfarm: main


node.ovc__vm:
    vdc: spacename
    ports: '80:80, 443:443, 18384:18384'
    sshkey: 'main
    os.image: 'Ubuntu 16.04 x64'

os.ssh.ubuntu__os:
    node: vm


```