from JumpScale import j


app = j.tools.cuisine._getBaseAppClass()


class CuisineVirtualBox(app):
    NAME = "virtualbox"

    def install(self, reset=False):

        from IPython import embed
        self.log("DEBUG NOW virtualbox")
        embed()
        raise RuntimeError("stop debug here")
