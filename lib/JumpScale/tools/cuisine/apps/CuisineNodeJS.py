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
        script = '''\
        cp /tmp/{version}/bin/node $binDir/
        mkdir -p $appDir/npm
        cp -r -t $appDir/npm /tmp/{version}/lib/node_modules/npm/*
        ln -s $appDir/npm/cli.js $binDir/npm
        '''.format(version=version)

        self._cuisine.core.execute_bash(script)
