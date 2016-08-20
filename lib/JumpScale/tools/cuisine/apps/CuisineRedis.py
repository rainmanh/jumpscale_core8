from JumpScale import j


from ActionDecorator import ActionDecorator


"""
please ensure that the start and build methods are separate and
the build doesnt place anyfile outside opt as it will be used in aysfs mounted system
"""


class actionrun(ActionDecorator):

    def __init__(self, *args, **kwargs):
        ActionDecorator.__init__(self, *args, **kwargs)
        self.selfobjCode = "cuisine=j.tools.cuisine.getFromId('$id');selfobj=cuisine.apps.redis"

base = j.tools.cuisine.getBaseClass()


class Redis(base):

    
    def build(self, name="main", ip="localhost", port=6379, maxram=200, appendonly=True, snapshot=False, slave=(), ismaster=False, passwd=None, unixsocket=True, start=True):
        # self._cuisine.installer.base()
        if self._cuisine.core.isUbuntu:

            C = """
            #!/bin/bash
            set -ex

            # groupadd -r redis && useradd -r -g redis redis

            mkdir -p $tmpDir/build/redis
            cd $tmpDir/build/redis
            wget http://download.redis.io/releases/redis-3.2.0.tar.gz
            tar xzf redis-3.2.0.tar.gz
            cd redis-3.2.0
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
            cp -f $tmpDir/build/redis/redis-3.2.0/src/redis-server $base/bin/
            cp -f $tmpDir/build/redis/redis-3.2.0/src/redis-cli $base/bin/

            rm -rf $base/apps/redis
            """
            C = self._cuisine.bash.replaceEnvironInText(C)
            C = self._cuisine.core.args_replace(C)
            self._cuisine.core.run_script(C)
        else:
            if self._cuisine.core.command_check("redis-server") == False:
                if self._cuisine.core.isMac:
                    self._cuisine.package.install("redis")
                else:
                    self._cuisine.package.install("redis-server")
            cmd = self._cuisine.core.command_location("redis-server")
            dest = "%s/redis-server" % self._cuisine.core.dir_paths["binDir"]
            if cmd != dest:
                self._cuisine.core.file_copy(cmd, dest)

        self._cuisine.bash.addPath(j.sal.fs.joinPaths(self._cuisine.core.dir_paths["base"], "bin"))

        redis_cli = j.clients.redis.getInstance(self._cuisine)
        redis_cli.configureInstance(name, ip, port, maxram=maxram, appendonly=appendonly,
                                    snapshot=snapshot, slave=slave, ismaster=ismaster, passwd=passwd, unixsocket=False)

        if start:
            self.start(name)

    
    def start(self, name="main"):
        dpath, cpath = j.clients.redis._getPaths(name)
        cmd = "$binDir/redis-server %s" % cpath
        self._cuisine.processmanager.ensure(name="redis_%s" % name, cmd=cmd, env={}, path='$binDir')
