from JumpScale import j


app = j.tools.cuisine._getBaseAppClass()


class CuisineMariadb(app):
    NAME = 'mariadb'

    def __init__(self, executor, cuisine):
        self._executor = executor
        self._cuisine = cuisine

    def install(self, start=False):
        self._cuisine.package.install("mariadb-server")
        if start:
            self.start()

    def start(self):
        pass
