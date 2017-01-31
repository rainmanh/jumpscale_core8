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
        while counter < 40:

            if j.do.TYPE.startswith("WIN"):
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

    def _start4JScore(self, j, tmpdir):
        """
        starts a redis instance in separate ProcessLookupError
        standard on $tmpdir/redis.sock
        """
        if j.do.TYPE.startswith("OSX"):
            #--port 0
            cmd = "redis-server --port 0 --unixsocket %s/redis.sock --maxmemory 100000000 --daemonize yes" % tmpdir
            print("start redis in background (osx)")
            os.system(cmd)
            print("started")
        elif j.do.TYPE.startswith("WIN"):
            cmd = "redis-server --maxmemory 100000000 & "
            print("start redis in background (win)")
            os.system(cmd)
        else:
            cmd = "echo never > /sys/kernel/mm/transparent_hugepage/enabled"
            os.system(cmd)
            cmd = "sysctl vm.overcommit_memory=1"
            os.system(cmd)
            redis_bin = '%s/bin/redis-server' % j.do.BASE
            if 'redis-server' not in os.listdir(path='%s/bin/' % j.do.BASE):
                url = "https://stor.jumpscale.org/public/redis-server"
                j.do.download(url, to=redis_bin, overwrite=False, retry=3)
            # import subprocess
            os.sync()
            j.sal.fs.chmod(redis_bin, 0o550)
            cmd = "%s  --port 0 --unixsocket %s/redis.sock --maxmemory 100000000" % (redis_bin, tmpdir)
            print("start redis in background (linux)")
            j.tools.cuisine.local.processmanager.ensure('redis_js', cmd)
