# Actor Templates, Actor & Service

## Actor templates

An actor template defines the full life cycle from pre-installation and installation to upgrades and monitoring of a service.

  More specifically an actor template describes:

- The parameters to configure a service
- How to configure the service
- How to get stats from the service
- How to export/import the data

All this is described in the actor template files:

- actor.hrd
- schema.hrd
- actions.py

## Actor

An _actor template_ becomes (or is "coverted" into) an _actor_ when it gets copied into a local repository, where it will be used for actually deploying one or more instances of the services.

Since an _actor_ is copied into an Repo, it is version controlled.

## Service

A _service_ is a deployed unique instance of an _actor_.

For example a Docker application running on a host node is an service instance of an actor template for that Docker application, for which there is a version-controlled actor specific to that environment.

Read the section about the [Life cycle of an service instance](AtYourServiceLifecycle.html) for more details.
