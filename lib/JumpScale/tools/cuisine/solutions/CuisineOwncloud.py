from JumpScale import j
from time import sleep


app = j.tools.cuisine._getBaseAppClass()


class CuisineOwncloud(app):
    NAME = 'owncloud'

    def __init__(self, executor, cuisine):
        self._executor = executor
        self._cuisine = cuisine

    def install(self, start=True):
        """
        install owncloud 9.1 on top of nginx/php/tidb
        tidb is the mysql alternative which is ultra reliable & distributed


        REQUIREMENT: nginx/php/tidb installed before
        """
        # TODO: *1
        if start:
            self.start("?")

    def start(self, name="???"):
        # TODO:*1
        pass

    def test(self):
        # call the api up/download a file
        pass
