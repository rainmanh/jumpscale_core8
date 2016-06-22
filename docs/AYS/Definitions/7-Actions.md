## AYS Actions

* Manages the life-cycle of your AYS
* you need to implement one or more methods (actions) on your atyourservice actions.py file

### Usage of arguments

Before the actions get executed the ays robot will apply the instance.hrd (is stored in ays instance directory) on the actions.py file

Example of instance.hrd

```python
description                    = 'life can be good in villa 77,\nIs for test purposes only.'
location                       = 'villa 78'
service.domain                 = 'ays'
service.name                   = 'datacenter'
service.version                = 
```

in actions.py each $(name) will get replaced

e.g.

```python
def somemethod(self):
  key = "$(service.domain)__$(service.name)__$(service.instance)"
  print(key)
  
```
this would print: ays__datacenter_palmlab

there are some default arguments

- $(service.instance)
- $(service.state.install) ... $(service.state.start ... )
  - the install/start/... are the action methods
  - knows states are: INIT,ERROR,OK,DISABLED,DO 


### Example:
 **actions.py** :
 
 these actions get executed where ays robot runs
 this file is stored in ays template dir

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


    def hrd(self, ayskey):
        """
        manipulate the hrd's after processing of the @ASK statements
        """


    def install(self, ayskey):
        """
        """
        return True

    def start(self, ayskey):
        """
        """
        return True

    def stop(self, ayskey):
        """
        """
        return True

    def halt(self, ayskey):
        """
        hard kill the app
        """
        return True

    def check_up(self, ayskey):
        """
        do checks to see if process(es) is (are) running.
        """
        return True

    def check_down(self, ayskey):
        """
        do checks to see if process(es) is down.
        """
        return True


    def check_requirements(self, ayskey):
        """
        do checks if requirements are met to install this app
        e.g. can we connect to database, is this the right platform, ...
        """
        return True

    def cleanup(self, ayskey):
        """
        regular cleanup of env e.g. remove logfiles, ...
        is just to keep the system healthy
        do not forget to schedule in your service.hrd or instance.hrd
        """
        return True

    def data_export(self, ayskey):
        """
        export data of app to a central location (configured in hrd under whatever chosen params)
        return the location where to restore from (so that the restore action knows how to restore)
        we remember in $name.export the backed up events (epoch,$id,$state,$location)  $state is OK or ERROR
        """
        return False

    def data_import(self,ayskey):
        """
        import data of app to local location
        """
        return False

    def uninstall(self, ayskey):
        """
        uninstall the apps, remove relevant files
        """
        pass

    def removedata(self, ayskey):
        """
        remove all data from the app (called when doing a reset)
        """
        pass


    def test(self, ayskey):
        """
        test the service on appropriate behavior
        """
        pass

    def build(self, ayskey):
        """
        build the service
        """
```