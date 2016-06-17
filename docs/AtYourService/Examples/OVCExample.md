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
