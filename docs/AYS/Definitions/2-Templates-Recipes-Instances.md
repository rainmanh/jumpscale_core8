# AYS Service Templates, Recipes & Instances

## AYS service templates

An AYS service template defines the full life cycle from pre-installation and installation to upgrades and monitoring of a service.

  More specifically an AYS service template describes:

- The parameters to configure a service
- How to configure the service
- How to get stats from the service
- How to export/import the data

All this is described in the AYS service template files:

- service.hrd
- schema.hrd
- actions.py

## AYS service recipes

An AYS service _template_ becomes (or is "coverted" into) an AYS service _recipe_ when it gets copied into a local AYS repository, where it will be used for actually deploying one or more instances of the services.

So an AYS service _recipe_ is exactly the same as an AYS service _template_, it's like a "snapshot" of the service template.

Since an AYS service _recipe_ is copied into an AYS Repo, it is version controlled.

## AYS service instances

An AYS service _instance_ is a deployed unique instance of an AYS _recipe_ - or AYS _template_.

For example a Docker application running on a host node is an AYS service instance of an AYS service template for that Docker application, for which there is a version-controlled AYS service recipe specific to that environment.

Read the section about the [Life cycle of an AYS service instance](AtYourServiceLifecycle.html) for more details.
