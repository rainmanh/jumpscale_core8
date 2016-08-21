from JumpScale import j

ActionsBaseNode = j.atyourservice.getActionsBaseClassNode()


class ActionsNode(ActionsBaseNode):
    """
    implement methods of this class to change behavior of lifecycle management of service
    """

    # def prepare(self):
    #     """
    #     this gets executed before the files are downloaded & installed on approprate spots
    #     """
    #     return True

    # def configure(self):
    #     """
    #     this gets executed when files are installed
    #     this step is used to do configuration steps to the platform
    #     after this step the system will try to start the service if anything needs to be started
    #     """
    #     return True

    # def start(self):
    #     """
    #     start happens because of info from main.hrd file but we can overrule this
    #     make sure to also call ActionBase.start(serviceObj) in your implementation otherwise the default behavior will not happen
    #     """
    #     return True

    # def stop(self):
    #     """
    #     if you want a gracefull shutdown implement this method
    #     a uptime check will be done afterwards (local)
    #     return True if stop was ok, if not this step will have failed & halt will be executed.
    #     """
    #     return True

    # def halt(self):
    #     """
    #     hard kill the app, std a linux kill is used, you can use this method to do something next to the std behavior
    #     """
    #     return True

    # def check_up(self,wait=True):
    #     """
    #     do checks to see if process(es) is (are) running.
    #     this happens on system where process is
    #     """
    #     return True

    # def check_down(self,wait=True):
    #     """
    #     do checks to see if process(es) are all down
    #     this happens on system where process is
    #     return True when down
    #     """
    #     return True

    # def check_requirements(self):
    #     """
    #     do checks if requirements are met to install this app
    #     e.g. can we connect to database, is this the right platform, ...
    #     """
    #     return True

    # def monitor(self):
    #     """
    #     do checks to see if all is ok locally to do with this package
    #     this happens on system where process is
    #     """
    #     return True

    # def cleanup(self):
    #     """
    #     regular cleanup of env e.g. remove logfiles, ...
    #     is just to keep the system healthy
    #     """
    #     return True

    # def data_export(self):
    #     """
    #     export data of app to a central location (configured in hrd under whatever chosen params)
    #     return the location where to restore from (so that the restore action knows how to restore)
    #     we remember in $name.export the backed up events (epoch,$id,$state,$location)  $state is OK or ERROR
    #     """
    #     return False

    # def data_import(self,id):
    #     """
    #     import data of app to local location
    #     if specifies which retore to do, id corresponds with line item in the $name.export file
    #     """
    #     return False

    # def uninstall(self):
    #     """
    #     uninstall the apps, remove relevant files
    #     """
    #     pass

    # def removedata(self):
    #     """
    #     remove all data from the app (called when doing a reset)
    #     """
    #     pass

    # def uninstall(self):
    #     """
    #     uninstall the apps, remove relevant files
    #     """
    #     pass

    # def test(self):
    #     """
    #     tests for the service to test its behavior
    #     """
    #     return True
