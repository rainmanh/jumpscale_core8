from JumpScale import j
from time import sleep


app = j.tools.cuisine._getBaseAppClass()


class CuisinePHP(app):
    NAME = 'nginx'

    def __init__(self, executor, cuisine):
        self._executor = executor
        self._cuisine = cuisine

    def _build(self):
        # TODO: *3 (optional)
        # build php with web modules
        raise NotImplementedError

    def install(self, start=True):
        """
        install, move files to appropriate places, and create relevant configs
        can use ubuntu apt's can learn from e.g. https://tjosm.com/4937/install-virtualmin-nginx-php-7-mariadb-ubuntu-16-04/ (dont need virtualmin)

        PHP inside nginx !!!

        also install
        - http://php.net/manual/en/install.fpm.php  (is this required for php 7.x?)
        - we probably need one or another accelerator? which one?

        QUESTION: which php version should we install (7.x?)


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
        # some php script, see it works
        raise NotImplementedError
