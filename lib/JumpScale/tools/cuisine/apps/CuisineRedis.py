from JumpScale import j


app = j.tools.cuisine._getBaseAppClass()


class CuisineRedis(app):
    NAME = 'redis-server'

    def build(self, reset=False):
        raise NotImplementedError()
        

    def install(self, reset=False):
        if reset == False and self.isInstalled():
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
            self._cuisine.core.run_script(C)
            
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
            self._cuisine.core.run_script(C)
        else:
            raise j.exceptions.NotImplemented(
                message="only ubuntu supported for building redis", level=1, source="", tags="", msgpub="")

    def start(self, name="main", ip="localhost", port=6379, maxram=200, appendonly=True,
              snapshot=False, slave=(), ismaster=False, passwd=None, unixsocket=True, start=True):
        # TODO: *1 lets carefully check this
        redis_cli = j.clients.redis.getInstance(self._cuisine)
        redis_cli.configureInstance(name, ip, port, maxram=maxram, appendonly=appendonly,
                                    snapshot=snapshot, slave=slave, ismaster=ismaster, passwd=passwd, unixsocket=False)
        dpath, cpath = j.clients.redis._getPaths(name)
        cmd = "$binDir/redis-server %s" % cpath
        self._cuisine.processmanager.ensure(name="redis_%s" % name, cmd=cmd, env={}, path='$binDir')
