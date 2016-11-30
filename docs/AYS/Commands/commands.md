# AYS Commands

## Help

- [help](help.md)

## Basic commands

the following commands show you the typical order in which you need to execute at your service
- [create_repo](create_repo.md) creates a new AYS repository
- [blueprint](blueprint.md) executes one or more blueprints, converting them into service instances
- [commit](commit.md) commits changes to the associated Git repository, allowing to keep track of changes
- [run](run.md) creates jobs (runs) for the scheduled actions, and proposes to start the jobs, which then executes the actions
- [simulate](simulate.md) allows you to see what will happen when executing an action, without actually having te execute it
- [destroy](destroy.md) destroys all service instances, from here you need to execute the blueprints again

## Advanced

- [delete](delete.md) deletes a service instances and all its children
- [discover](discover.md) discovers an AYS repository on the filesystem
- [restore](restore.md) loads an AYS service instance from the filesystem
- [run_info](run_info.md) displays information about a run/job
- [do](do.md) is a helper method to easily schedule actions from the command line
- [list](list.md) lists all service instances
- [repo_list](repo_list.md) lists all known repositories
- [update](update.md) updates an actor to the new version
- [test](test.md) runs AYS tests
- [show](show.md) shows information about a service instance
- [state](state.md) displays the state of a service instance
- [set_state](set_state.md) manually sets the state of a service action
