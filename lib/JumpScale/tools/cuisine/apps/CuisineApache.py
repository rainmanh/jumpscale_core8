from JumpScale import j
import textwrap

app = j.tools.cuisine._getBaseAppClass()


class CuisineApache(app):

    NAME = 'httpd'

    def build(self):
        return True

    def install(self):
        self._cuisine.package.ensure("apache")

    def start(self):
        """start Apache."""
        self._cuisine.core.run("apachectl start")

    def stop(self):
        """stop Apache."""
        self._cuisine.core.run("apachectl stop")

    def restart(self):
        """restart Apache."""
        self._cuisine.core.run("apachectl restart")
