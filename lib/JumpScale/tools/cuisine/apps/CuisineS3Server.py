from JumpScale import j
from time import sleep


app = j.tools.cuisine._getBaseAppClass()


class CuisineS3Server(app):
    NAME = 's3server'

    def __init__(self, executor, cuisine):
        self._executor = executor
        self._cuisine = cuisine

    def _build(self):
        # TODO: *1
        # build
        raise NotImplementedError

    def install(self, start=True):
        """


        put backing store on /storage/...

        """
        # TODO: *1
        if start:
            self.start("?")

    def build(self, start=True, install=True):
        self._build()
        if install:
            self.install(start)

    def start(self, name="???"):
        # TODO:*1
        raise NotImplementedError

    def test(self):
        # host a file test can be reached
        raise NotImplementedError
