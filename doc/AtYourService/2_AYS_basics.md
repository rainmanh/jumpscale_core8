### AtYourService Basics

#### AYS repos

- Are git based repo's, they store the templates or the actual deployment
- 2 types
    - ays template repo = templates which can be used to start from
    - ays repo = where install/deployment/monitoring happens
    - see [AYS File Locations](AtYourServiceFileLocations.md)

#### AYS Templates, Recipes and Instances

*AYS Template*

- Defines the full life cycle from pre-installation, over installation, to upgrades and monitoring of a service, all described in the template files:
    - service.hrd
    - schema.hrd
    - action*.py (2 types of action files)
- In a recipe we describe
    - Parameters relevant for a service instance
    - How to start/stop the instance
    - How to monitor the instance
    - How to configure the instance
    - How to get stats from the instance
    - How to export/import the data


*AYS Recipe*

- Recipe's are the same as AYS Templates but they get copied into the AYS Repository.
- We copy these files to make sure they get version controlled together with the AYS Instances.
- The have the same content as the templates!

*Instances*

In instance is a deployed unique instance of an AtYourService.
E.g. a docker application running on a host node, the application would be the service.

The instances are 

#### Blueprints



Example :
```
redis_redis1:
  description:
    - "a description"

redis_redis2:
  description:
    - "a description"

myapp_test:
  redis: 'redis1, redis2'

```



#### Each AtYourService instance has a unique key

Key in format $domain|$name!$instance@role ($version)

Different format examples
+ $domain|$name!$instance
+ $name
+ !$instance
+ $name!$instance
+ @role

Version is added with ()
+ e.g. node.ssh (1.0), where "node.ssh" is the name of the service, which in this case contains a "." where "node" is the role of the service and "ssh" the name of the instance

### AYS instances can be found using this key format

e.g.
```shell
#find 1 service instance with role MongoDB and then start (if not started yet), if more than 1 then this will fail
ays start -n @mongodb

#find all service instances with role node and print their status
ays status -n @node

#find a service instance which has instance name ovh4
ays status -n !ovh4

```

If more than 1 instance is found then there will be an error

### Each service has a role

Role is first part of name, e.g. if the AYS service name is "node.ssh" the role = node

Roles are used to define categories of AYS recipes e.g. AYS which define a node & how to execute commands on a node, another example of a role is e.g. ns

### Init redis local or remote (example)

local

```
ays init -n redis -i --data 'param.name:system param.port:7766 param.disk:0  param.mem:100 param.ip:127.0.0.1 param.unixsocket:0 param.passwd:'
```

remote

```
ays init -n node.ssh -i ovh4 --data "ip:94.13.18.89 ssh.port:22"

ays init -n redis -i system --parent '!ovh4' --data 'param.name:system param.port:7766 param.disk:0  param.mem:100 param.ip:127.0.0.1 param.unixsocket:0 param.passwd:'

```

Notice how we use as key !ovh4 this means any ays with instance name ovh4 will be used (only if found 1)
more complete way to specify would have been 'node.ssh!ovh4' or '!ovh4$node' #means instance ovh4 from role node

Remark: install will only happen after 'ays apply'

### Producers & Consumers

- Each service instance can consume a service delivered by a producer
- A producer is another service instance delivering a service
- The consumption of another service is specified in the schema.hrd file
    - see [HRD](HRD.md) by keyword consume
    - there is a special type of consumption which is called a parent, this defines our location in the ays repo filesystem (visualization) but also a child/parent relationship e.g. an app living inside a node.


### Some special AtYourService recipe args

```
ns.enable = True
```

- ns.enable means we will be using the nameservice service, is not relevant for all services


### AtYourService Actions

> This part is deprecated and need revision @rthursday @zaibon

some remarks
- the management actions as defined in actions_mgmt are always executed on server which is executing starting from the ays repo (the checkout out git repo)
- the node actions are always executed on the node where the action needs to happen

#### init

- is the first action to be done, this action will init your repo with the required instances
- process
    - copy template files to appropriate destination (in your ays repo e.g. /Users/kristofdespiegeleer1/code/jumpscale/ays_core_it/services/sshkey!main)
    - call actions.input
        - goal is to manipulate the arguments which are the basis of the instance.hrd, this allows the system to avoid questions to be asked during install (because of @ASK statements in the instance.hrd files)
        - in actions.input manipulate the 'args' argument to the method
        - return True if action was ok
        - ask the non configured items from schema.hrd (the @ASK commands, the ones not filled in in previous step
    - call actions.hrd
        - now the @ASK is resolved and the input arguments, this step allows to further manipulate the hrd files
        - examples: create an ssh key and store in hrd file
        - after this action the ays directory is up to date with all required configuration information
        - information outside can be used to get info in hrd e.g. stats info from reality db
    - apply all instance & service.hrd arguments on the action files in the deployed ays instance directory
        - this means that all action files have all template arguments filled in

### consume


- 3 ways this can be done
    - ```es=j.atyourservice.new(name='energyswitch', args=data, parent=location, consume=grid)```
    - ```es.consume("grid")``` the services was already created before
    - ```ays consume -n energyswitch!main -c grid``` #@todo
- this specified how services depend on other services
- the actions.consume action will be called
- in blueprint a consumption can be specified by just filling in the appropriate property e.g. datacenter=gent if in the scheme datacenter was a possible e.g. parent

#### install

- deploys the ays on the node
- process
    - call actions_mgmt.install_pre
    - call actions_node.prepare (will do e.g. installation of ubuntu services, better not to use)
    - call actions_node.install
    - call actions_mgmt.install_post
        - its up to ays developer to call start method ...
        - in this post action you can ask ```serviceObj.getNodeHrd()``` which will fetch the hrd back from node to mgmt side

#### start/stop/export/import/....

- calls specific actions in mgmt side (git repo) and node
    - $name is the name of the action e.g. stop
- process
    - call actions_mgmt.$name_pre
    - call actions_node.$name
    - call actions_mgmt.$name_post
        - in this post action you can ask ```serviceObj.getNodeHrd()``` which will fetch the hrd back from node to mgmt side
