
from JumpScale import j

class CuisineUpstart():

    def __init__(self,executor,cuisine):
        self.executor=executor
        self.cuisine=cuisine

    
    def ensure(self,name):
        """Ensures that the given upstart service is self.running, starting
        it if necessary."""
        status = self.cuisine.sudo("service %s status" % name,warn_only=True)
        if status.failed:
            status = self.cuisine.sudo("service %s start" % name)
        return status

    def reload(self,name):
        """Reloads the given service, or starts it if it is not self.running."""
        status = self.cuisine.sudo("service %s reload" % name,warn_only=True)
        if status.failed:
            status = self.cuisine.sudo("service %s start" % name)
        return status

    def restart(self,name):
        """Tries a `restart` command to the given service, if not successful
        will stop it and start it. If the service is not started, will start it."""
        status = self.cuisine.sudo("service %s status" % name,warn_only=True)
        if status.failed:
            return self.cuisine.sudo("service %s start" % name)
        else:
            status = self.cuisine.sudo("service %s restart" % name)
            if status.failed:
                self.cuisine.sudo("service %s stop"  % name)
                return self.cuisine.sudo("service %s start" % name)
            else:
                return status

    def stop(self,name):
        """Ensures that the given upstart service is stopped."""
        status = self.cuisine.sudo("service %s status" % name,warn_only=True)
        if status.succeeded:
            status = self.cuisine.sudo("service %s stop" % name)
        return status