## AYS Service Templates, Recipes & Instances

### AYS service templates

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

### AYS service recipes

An AYS service *template* becomes (or is "coverted" into) an AYS service *recipe* when it gets copied into a local AYS repository, where it will be used for actually deploying one or more instances of the services.

So an AYS service *recipe* is exactly the same as an AYS service *template*, it's like a "snapshot" of the service template.  

Since an AYS service *recipe* is copied into an AYS Repo, it is version controlled.


### AYS service instances

An AYS service *instance* is a deployed unique instance of an AYS *recipe* - or AYS *template*.

For example a Docker application running on a host node is an AYS service instance of an AYS service template for that Docker application, for which there is a version-controlled AYS service recipe specific to that environment.