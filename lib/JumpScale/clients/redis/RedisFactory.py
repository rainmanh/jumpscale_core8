# from JumpScale import j

# import redis
# from JumpScale.baselib.credis.CRedis import CRedis

from JumpScale.clients.redis.Redis import Redis
from JumpScale.clients.redis.RedisQueue import RedisQueue
import os
import time

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

    def get(self, ipaddr, port, password="", fromcache=True):
        key = "%s_%s" % (ipaddr, port)
        if not fromcache:
            return Redis(ipaddr, port, password=password)
        if key not in self._redis:
            self._redis[key] = Redis(ipaddr, port, password=password)
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

        if j.do.TYPE.startswith("WIN"):
            j.core.db = Redis()
        else:
            j.core.db = Redis(unix_socket_path='%s/redis.sock' % tmpdir)

        try:
            j.core.db.set("internal.last", 0)
        except Exception as e:
            print("warning:did not find redis")
            j.core.db = None

        if j.core.db is None:
            self.start4JScore(j, tmpdir)

    def start4JScore(self, j, tmpdir):
        """
        starts a redis instance in separate ProcessLookupError
        standard on $tmpdir/redis.sock
        """
        if j.do.TYPE.startswith("OSX"):
            #--port 0
            cmd = "redis-server --unixsocket %s/redis.sock --maxmemory 100000000 --daemonize yes" % tmpdir
            print("start redis in background (osx)")
            os.system(cmd)
        elif j.do.TYPE.startswith("WIN"):
            cmd = "redis-server --maxmemory 100000000 & "
            print("start redis in background")
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
            sync_cmd = 'sync'
            cmd1 = "chmod 550 %s 2>&1" % redis_bin
            cmd2 = "%s  --port 0 --unixsocket %s/redis.sock --maxmemory 100000000 --daemonize yes" % (redis_bin, tmpdir)
            print("start redis in background")
            os.system(cmd1)
            os.system(sync_cmd)
            os.system(cmd2)
        # Wait until redis is up

        while j.core.db is None:
            self.init4jscore(j, tmpdir)
            time.sleep(0.1)
