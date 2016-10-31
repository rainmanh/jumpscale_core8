from JumpScale import j


app = j.tools.cuisine._getBaseAppClass()


class CuisineVirtualBox(app):
    NAME = "virtualbox"

    def __init__(self, executor, cuisine):
        self._executor = executor
        self._cuisine = cuisine

    def install(self, reset=False):

        from IPython import embed
        print("DEBUG NOW virtualbox")
        embed()
        raise RuntimeError("stop debug here")
