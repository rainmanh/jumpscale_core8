# from JumpScale import j

# import redis
# from JumpScale.baselib.credis.CRedis import CRedis

from JumpScale.clients.redis.Redis import Redis
from JumpScale.clients.redis.RedisQueue import RedisQueue
import os
import time
import sys
# import itertools


class RedisFactory:

    """
    """

    def __init__(self):
        # self.__jslocation__ = "j.clients.redis"
        self.clearCache()

    def clearCache(self):
        self._redis = {}
        self._redisq = {}
        self._config = {}

    def get(self, ipaddr="localhost", port=6379, password="", fromcache=True, unixsocket=None):
        if unixsocket is None:
            key = "%s_%s" % (ipaddr, port)
        else:
            key = unixsocket
        if key not in self._redis or not fromcache:
            if unixsocket is None:
                self._redis[key] = Redis(ipaddr, port, password=password)  # , unixsocket=unixsocket)
            else:
                self._redis[key] = Redis(unix_socket_path=unixsocket, password=password)

        return self._redis[key]

    def getQueue(self, ipaddr, port, name, namespace="queues", fromcache=True):
        if not fromcache:
            return RedisQueue(self.get(ipaddr, port, fromcache=False), name, namespace=namespace)
        key = "%s_%s_%s_%s" % (ipaddr, port, name, namespace)
        if key not in self._redisq:
            self._redisq[key] = RedisQueue(
                self.get(ipaddr, port), name, namespace=namespace)
        return self._redisq[key]

    def init4jscore(self, j, tmpdir):
        """
        will try to create redis connection to $tmpdir/redis.sock
        if not found will then try to start the redis server
        """
        tmpdir = tmpdir.rstrip("/")

        counter = 0
        while counter < 10:
            pl = sys.platform.lower()
            if 'w32' in pl or 'w64' in pl or 'win' in pl and not "darwin" in pl:
                j.core.db = Redis()
            else:
                j.core.db = Redis(unix_socket_path='%s/redis.sock' % tmpdir)

            try:
                j.core.db.set("internal.last", 0)
                return True
            except Exception as e:

                # Todo
                if False and "redis.sock. No such file or directory" in str(e):
                    tempRedis = Redis()
                    try:
                        tempRedis.set("internal.last", 0)
                        print("PLEASE KILL ALL REDIS INSTANCES")
                        counter = 40
                    except Exception as e:
                        pass
                else:
                    print("warning:did not find redis")
                    print("error:%s" % e)
                    j.core.db = None

            if j.core.db is None:
                self._start4JScore(j, tmpdir)
                time.sleep(0.5)
                counter += 1

        print("could not start redis server, check manually, best to kill all of them and restart.")
        sys.exit(1)

    def kill(self):
        j.do.execute("redis-cli -s %s/redis.sock shutdown" % j.do.TMPDIR, die=False, showout=False, outputStderr=False)
        j.do.execute("redis-cli shutdown", die=False, showout=False, outputStderr=False)
        j.do.killall("redis")

    def _start4JScore(self, j, tmpdir):
        """
        starts a redis instance in separate ProcessLookupError
        standard on $tmpdir/redis.sock
        """
        if j.tools.cuisine.local.core.isMac:
            if not j.do.checkInstalled("redis-server"):
                j.do.execute("brew unlink redis;brew install redis;brew link redis")
            if not j.do.checkInstalled("redis-server"):
                raise RuntimeError("Cannot find redis-server even after install")
            j.do.execute("redis-cli -s %s/redis.sock shutdown" %
                         j.do.TMPDIR, die=False, showout=False, outputStderr=False)
            j.do.execute("redis-cli shutdown", die=False, showout=False, outputStderr=False)
            j.do.killall("redis")
            cmd = "redis-server --port 6379 --unixsocket %s/redis.sock --maxmemory 100000000 --daemonize yes" % tmpdir  # 100MB
            print("start redis in background (osx)")
            os.system(cmd)
            print("started")
            time.sleep(1)

        elif j.tools.cuisine.local.core.isCygwin:
            cmd = "redis-server --maxmemory 100000000 & "
            print("start redis in background (win)")
            os.system(cmd)
        elif j.tools.cuisine.local.core.isLinux:
            cmd = "echo never > /sys/kernel/mm/transparent_hugepage/enabled"
            os.system(cmd)
            cmd = "sysctl vm.overcommit_memory=1"
            os.system(cmd)
            redis_bin = '%s/bin/redis-server' % j.dirs.base
            if 'redis-server' not in os.listdir(path='%s/bin/' % j.dirs.base):
                url = "https://stor.jumpscale.org/public/redis-server"
                j.tools.cuisine.local.core.file_download(url, to=redis_bin, overwrite=False, retry=3)
            # import subprocess
            sync_cmd = 'sync'
            cmd1 = "chmod 550 %s 2>&1" % redis_bin
            cmd2 = "%s  --port 0 --unixsocket %s/redis.sock --maxmemory 100000000 --daemonize yes" % (redis_bin, tmpdir)
            print("start redis in background (linux)")
            os.system(cmd1)
            os.system(sync_cmd)
            os.system(cmd2)
        else:
            raise RuntimeError("platform not supported")
