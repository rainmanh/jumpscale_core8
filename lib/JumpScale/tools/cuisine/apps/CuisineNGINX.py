from JumpScale import j
from time import sleep


app = j.tools.cuisine._getBaseAppClass()


class CuisineNGINX(app):
    NAME = 'nginx'

    def __init__(self, executor, cuisine):
        self._executor = executor
        self._cuisine = cuisine

    def _build(self):
        # TODO: *3 optional
        # build nginx
        raise NotImplementedError

    def install(self, start=True):
        """
        can install through ubuntu

        """
        # TODO: *1 symlink or copy files to $appDir/nginx/
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
