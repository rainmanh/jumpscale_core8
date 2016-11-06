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
        self._cuisine.package.mdupdate()
        self._cuisine.package.install('xz-utils')

        version = 'node-v6.7.0-linux-x64'
        url = 'https://nodejs.org/dist/v6.7.0/{}.tar.xz'.format(version)
        dest = '/tmp/node.tar.xz'
        self._cuisine.core.run('curl -o {} {}'.format(dest, url))
        self._cuisine.core.run('tar --overwrite -xf {} -C /tmp/'.format(dest))

        # copy file to correct locations.
        self._cuisine.core.dir_ensure('$binDir')
        self._cuisine.core.dir_ensure('$appDir/npm')
        src = '/tmp/{version}/bin/node'.format(version=version)
        self._cuisine.core.file_copy(src, '$binDir', recursive=True, overwrite=True)
        src = '/tmp/{version}/lib/node_modules/npm/*'.format(version=version)
        self._cuisine.core.file_copy(src, '$appDir/npm', recursive=True, overwrite=True)
        if self._cuisine.core.file_exists('$binDir/npm'):
            self._cuisine.core.file_unlink('$binDir/npm')
        self._cuisine.core.file_link('$appDir/npm/cli.js', '$binDir/npm')
