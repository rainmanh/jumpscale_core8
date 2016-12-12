from JumpScale import j

app = j.tools.cuisine._getBaseAppClass()


class CuisineRust(app):
    NAME = 'rust'

    def __init__(self, executor, cuisine):
        self._executor = executor
        self._cuisine = cuisine

    def install(self):
        """
        https://static.rust-lang.org/dist/rust-1.12.0-x86_64-unknown-linux-gnu.tar.gz
        """

        version = 'rust-nightly-x86_64-unknown-linux-gnu'
        url = 'https://static.rust-lang.org/dist/{}.tar.gz'.format(version)
        dest = '/tmp/rust.tar.gz'
        self._cuisine.core.run('curl -o {} {}'.format(dest, url))
        self._cuisine.core.run('tar --overwrite -xf {} -C /tmp/'.format(dest))

        # copy file to correct locations.
        self._cuisine.core.run('cd /tmp/{version} && ./install.sh --prefix=$JSAPPDIR/rust --destdir==$JSAPPDIR/rust'.format(version=version))

        self._cuisine.bash.addPath(self._cuisine.core.args_replace('$JSAPPDIR/rust/bin'))
