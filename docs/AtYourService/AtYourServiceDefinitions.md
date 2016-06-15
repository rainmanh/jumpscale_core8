### AtYourService Definitions

#### AYS repos

Are git based repos, they store the templates or the actual deployment
There are two types of AYS repos:
   - ays service template repo: templates which can be used in a blueprint
   - ays repo: where installation/deployment/monitoring happens
   
(see [AYS File Locations](AtYourServiceFileLocations.md))

#### Blueprints
A blueprint a [yaml](http://yaml.org/) file that is the entry point to interacting with AYS. It describes how the deployment should look like.

An example of a blueprint `1_example.yaml`:
```
  redis__redis1:
    description:
      - "a description"

  redis_redis2:
    description:
      - "a description"

  myapp_test:
    redis: 'redis1, redis2'

```

#### AYS Templates, Recipes and Instances

- ##### *AYS Recipe*

  When using blueprints the ays recipe is automatically created.
  
  An AYS recipe defines the full life cycle from pre-installation, over installation, to upgrades and monitoring of a service, all described in the recipe files:
    - service.hrd
    - schema.hrd
    - actions.py

  In a recipe we describe
    - Parameters relevant for a service instance
    - How to start/stop the instance
    - How to monitor the instance
    - How to configure the instance
    - How to get stats from the instance
    - How to export/import the data
    - How to perform any of the other actions described in the template.


- ##### *Instances*

  Instances that will be consumed and/or created are defined inside the blueprint. In the above example, `redis1`, `redis2` and `test` are the instances of the `redis` and `myapp` servicetemplates.

@todo kerwyny complete please


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

Roles are used to define categories of AYS recipes e.g. AYS which define a node & how to execute commands on a node.


### Producers & Consumers

- Each service instance is a producer of its own role
- Each service instance can consume a service delivered by a producer
- The consumption of another service is specified in the schema.hrd file
    - see [HRD](HRD.md) by keyword consume
    - there is a special type of consumption which is called a parent, this defines our location in the ays repo filesystem (visualization) but also a child/parent relationship e.g. an app living inside a node.


  - There are different ways this can be done:
      - ```es = j.atyourservice.new(name='energyswitch', args=data, parent=location, consume=grid)```
      - ```es.consume("grid")``` the services was already created before
  - This relationship specifies how services depend on other services
  - The actions.consume action will be called
  - In blueprint a consumption can be specified by just filling in the appropriate property e.g. datacenter=gent if in the scheme datacenter was a possible e.g. parent


### AtYourService Actions
- #### init

  This is the first action to be taken on an ays repo, it will initialize your repo with the required instances.
  
  What happens during `init`:
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

- #### install

  deploys the ays instances

- #### start/stop/monitor/....

  