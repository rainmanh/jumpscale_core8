from JumpScale import j


app = j.tools.cuisine._getBaseAppClass()


class CuisineRedis(app):
    NAME = 'redis-server'

    def build(self, reset=False, start=False):
        """Building and installing redis"""
        if reset is False and self.isInstalled():
            print('Redis is already installed, pass reset=True to reinstall.')
            return

        if self._cuisine.core.isUbuntu:
            self._cuisine.package.update()
            self._cuisine.package.install("build-essential")

            C = """
            #!/bin/bash
            set -ex

            # groupadd -r redis && useradd -r -g redis redis

            mkdir -p $tmpDir/build/redis
            cd $tmpDir/build/redis
            wget http://download.redis.io/redis-stable.tar.gz
            tar xzf redis-stable.tar.gz
            cd redis-stable
            make

            rm -f /usr/local/bin/redis-server
            rm -f /usr/local/bin/redis-cli
            """
            C = self._cuisine.bash.replaceEnvironInText(C)
            C = self._cuisine.core.args_replace(C)
            self._cuisine.core.execute_bash(C)

            # move action
            C = """
            set -ex
            mkdir -p $base/bin/
            cp -f $tmpDir/build/redis/redis-stable/src/redis-server $base/bin/
            cp -f $tmpDir/build/redis/redis-stable/src/redis-cli $base/bin/
            rm -rf $base/apps/redis
            """
            C = self._cuisine.bash.replaceEnvironInText(C)
            C = self._cuisine.core.args_replace(C)
            self._cuisine.core.execute_bash(C)
        else:
            raise j.exceptions.NotImplemented(
                message="only ubuntu supported for building redis", level=1, source="", tags="", msgpub="")

        if start is True:
            self.start()

    def isInstalled(self):
        return self._cuisine.core.command_check('redis-server') and self._cuisine.core.command_check('redis-cli')

    def install(self, reset=False):
        return True

    def start(self, name="main", ip="localhost", port=6379, maxram=1048576, appendonly=True,
              snapshot=False, slave=(), ismaster=False, passwd=None, unixsocket=None):
        redis_cli = j.sal.redis.getInstance(self._cuisine)
        redis_cli.configureInstance(name,
                                    ip,
                                    port,
                                    maxram=maxram,
                                    appendonly=appendonly,
                                    snapshot=snapshot,
                                    slave=slave,
                                    ismaster=ismaster,
                                    passwd=passwd,
                                    unixsocket=unixsocket)
        # return if redis is already running
        if redis_cli.isRunning(ip_address=ip, port=port, path='$binDir', password=passwd, unixsocket=unixsocket):
            print('Redis is already running!')
            return

        _, cpath = j.sal.redis._getPaths(name)

        cmd = "$binDir/redis-server %s" % cpath
        self._cuisine.processmanager.ensure(name="redis_%s" % name, cmd=cmd, env={}, path='$binDir')

        # Checking if redis is started correctly with port specified
        if not redis_cli.isRunning(ip_address=ip, port=port, path='$binDir', unixsocket=unixsocket):
            raise j.exceptions.RuntimeError('Redis is failed to start correctly')

    def stop(self, name='main'):
        self._cuisine.processmanager.stop(name="redis_%s" % name)
