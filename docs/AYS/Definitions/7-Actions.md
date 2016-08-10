# AYS Actions

- Manages the life cycle of your AYS
- you need to implement one or more methods (actions) on your atyourservice actions.py file

## Usage of arguments

Before the actions get executed AYS will apply the `instance.hrd` (as stored in AYS instance directory) on the `actions.py` file.

Example of an `instance.hrd`:

```python
description                    = 'life can be good in villa 77,\nIs for test purposes only.'
location                       = 'villa 78'
service.domain                 = 'ays'
service.name                   = 'datacenter'
service.version                =
```

In `actions.py` each `$(name)` will get replaced, e.g.:

```python
def somemethod(self):
  key = "$(service.domain)__$(service.name)__$(service.instance)"
  print(key)
```

This would print: `ays__datacenter_palmlab`

## Example:

**actions.py**:

These actions get executed when the AYS robot runs. This file is stored in the AYS template directory:

```python
class ActionsBaseMgmt:
    """
    implement methods of this class to change behavior of lifecycle management of service
    this one happens at central side from which we coordinate our efforts
    """

    def input(self,name,role,instance,args={}):
        """

        gets executed before init happens of this ays

        use this method to manipulate the arguments which are given or already part of ays instance
        this is done as first action on an ays, at central location

        example how to use

        if name.startswith("node"):
            args["something"]=111

        make sure to return args

        """
        return args

    def init(self, service):
        """
        First action executed during the instanciation of a service template to a service instance.
        """


    def hrd(self, service):
        """
        manipulate the hrd's after processing of the @ASK statements
        """


    def install(self, service):
        """
        """
        return True

    def start(self, service):
        """
        """
        return True

    def stop(self, service):
        """
        """
        return True

    def halt(self, service):
        """
        hard kill the app
        """
        return True

    def check_up(self, service):
        """
        do checks to see if process(es) is (are) running.
        """
        return True

    def check_down(self, service):
        """
        do checks to see if process(es) is down.
        """
        return True


    def check_requirements(self, service):
        """
        do checks if requirements are met to install this app
        e.g. can we connect to database, is this the right platform, ...
        """
        return True

    def cleanup(self, service):
        """
        regular cleanup of env e.g. remove logfiles, ...
        is just to keep the system healthy
        do not forget to schedule in your service.hrd or instance.hrd
        """
        return True

    def data_export(self, service):
        """
        export data of app to a central location (configured in hrd under whatever chosen params)
        return the location where to restore from (so that the restore action knows how to restore)
        we remember in $name.export the backed up events (epoch,$id,$state,$location)  $state is OK or ERROR
        """
        return False

    def data_import(self,service):
        """
        import data of app to local location
        """
        return False

    def uninstall(self, service):
        """
        uninstall the apps, remove relevant files
        """
        pass

    def removedata(self, service):
        """
        remove all data from the app (called when doing a reset)
        """
        pass


    def test(self, service):
        """
        test the service on appropriate behavior
        """
        pass

    def build(self, service):
        """
        build the service
        """
```
