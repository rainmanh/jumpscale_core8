## AtYourService Basics

### AYS Repositories

AYS repositories (repos) are Git repositories related to a service of which the full life cycle can be managed by AYS.

There are two types of repos used by AYS:

- **AYS Template Repos**
    Git repositories containing all data (templates) from which an actual AYS instance can be deployed
- **AYS Repos**
    Git repositories containing actually deployed instances

See [AYS File Locations](AtYourServiceFileLocations.md) for more details.


### AYS service templates, recipes and instances

#### AYS service templates

An AYS service template defines the full life cycle from pre-installation and installation to upgrades and monitoring of a service.

More specifically an AYS service template describes:
  - The Parameters to configure a service
  - How to start/stop the service
  - How to monitor the service
  - How to configure the service
  - How to get stats from the service
  - How to export/import the data

All this is described in the AYS service template files:
  - service.hrd
  - schema.hrd
  - actions.py
    
Read the section about the [Life cycle of an AYS service instance](AtYourServiceLifecycle.html) for more details.


#### AYS service recipes

An AYS service *template* becomes (or is "coverted" into) an AYS service *recipe* when it gets copied into a local AYS repository, where it will be used for actually deploying one or more instances of the services.

So an AYS service *recipe* is exactly the same as an AYS service *template*, it's like a "snapshot" of the service template.  

Since an AYS service *recipe* is copied into an AYS Repo, it is version controlled.


#### AYS service instances

An AYS service *instance* is a deployed unique instance of an AYS *recipe* - or AYS *template*.

For example a Docker application running on a host node is an AYS service instance of an AYS service template for that Docker application, for which there is a version-controlled AYS service recipe specific to that environment.


### AYS blueprints

An AYS *blueprint* is a [YAML](http://yaml.org/) file used as the entry point for interacting with AYS. It describes the deployment of a specific application.

It does so by defining all service instances that make up a specific application and how these AYS services instances interact with each other.

Example:

```yaml
redis_redis1:
  description:
    - "a description"

redis_redis2:
  description:
    - "a description"

myapp_test:
  redis: 'redis1, redis2'
```

The above example is about the `test` application using two instances of the `Redis`.


### Each AYS service has a name, a role and a version.

The *role* is the first part of name, and the version is added with ().

For example in `node.ssh (1.0)`:
- The name of the service is `node.ssh`, which in this case contains a `.` (dot) separating `node` as the role of the service and `ssh` the name of the instance
- The version is 1.0

Roles are used to define categories of AYS service recipes.


### Each AYS service instance has a unique key

This unique key is formatted as `$domain|$name!$instance@role ($version)`

You can select one or more service instances by using the full key and just parts of the key:

+ $domain|$name!$instance
+ $name
+ !$instance
+ $name!$instance
+ @role


### Producers & consumers

Each service instance can consume a service delivered by a producer. A producer is another service instance delivering a service.

The consumption of another service is specified in the `schema.hrd` file of a service template ore recipe, using the `consunme` keyword. 

As an example of consumption, see the following `schema.hrd` specification:

```yaml
sshkey = descr:'authorized sshkey' consume:sshkey:1:2 auto
```

This describes that the service consumes a minimum of `1` and a maximum of `2` sshkey instances,  and that it should auto-create these instances if they don't already exist. Minimum and maximum tags are optional. As well as `auto`.

See the section about [HRD](../BeyondBasics/HRD.html) files for more details.


### Parents

There is a special type of consumption which is called a *parent*.

This defines the location in the AYS repo file system (visualization) but also a child/parent relationship, e.g. an app living inside a node.

Child services also inherit their parents executor defined in `getExecutor` by default.

Example of parents in `schema.hrd`:

```yaml
node = type:str parent:node auto
```

This means that the service has a parent of role `node` and that it should auto create its parent if it doesn't already exist. The `auto` tag is optional.


### AYS actions

AYS actions define the behavior of an AYS service, including the full life cycle.

Read the section about [Actions](5_AYS_actions.html) for more details.