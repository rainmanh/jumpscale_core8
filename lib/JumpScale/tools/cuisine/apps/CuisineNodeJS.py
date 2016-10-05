from JumpScale import j

app = j.tools.cuisine._getBaseAppClass()


class CuisineNodeJS(app):
    NAME = 'nodejs'

    def __init__(self, executor, cuisine):
        self._executor = executor
        self._cuisine = cuisine

    def install(self):
        """
        can install through ubuntu
        """

        self._cuisine.package.ensure('nodejs')
        self._cuisine.package.ensure('npm')
        self._cuisine.core.file_link('/usr/bin/nodejs', '/usr/bin/node')

        # TODO: copy files back to $appDir/nodejs
