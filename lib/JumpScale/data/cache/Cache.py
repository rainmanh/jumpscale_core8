
from JumpScale import j

import time

class Cache:

    def __init__(self):
        self.__jslocation__ = "j.data.cache"
        self._cache = {}

    def get(self, id="main", db=None, reset=False,expiration=360):
        """
        @param id is a unique id for the cache
        db = when none then will be in memory
        """
        if db==None:
            db=j.servers.kvs.getMemoryStore(name=id, namespace="cache")
        if id not in self._cache:
            self._cache[id] = CacheCategory(id=id, db=db,expiration=expiration)
        if self._cache[id].db.name!=db.name or self._cache[id].db.namespace!=db.namespace :
            self._cache[id] = CacheCategory(id=id, db=db,expiration=expiration)
        if reset:
            self.reset(id)
        return self._cache[id]

    def resetAll(self):
        for key, cache in self._cache.items():
            cache.reset()

    def reset(self, id):
        if id in self._cache:
            self._cache[id].reset()

    def test(self):

        def testAll(c):
            c.reset()
            c.set("something", "OK")
            assert "OK" == c.get("something")

            def return1():
                return 1

            def return2():
                return 2

            assert c.get("somethingElse", return1) == 1
            assert c.get("somethingElse") == 1

            c.reset()

            try:
                c.get("somethingElse")
            except Exception as e:
                if not "Cannot get 'somethingElse' from cache" in str(e):
                    raise RuntimeError("error in test. non expected output")


            print("expiration test")
            time.sleep(2)

            try:
                assert c.get("somethingElse",return2) == 2
            except Exception as e:
                from IPython import embed
                print ("DEBUG NOW 98")
                embed()
                raise RuntimeError("stop debug here")


        c = self.get("test",j.servers.kvs.getRedisStore(name='cache', namespace="mycachetest"),expiration=1)
        testAll(c)
        c = self.get("test", j.servers.kvs.getMemoryStore(name='cache', namespace="mycachetest"),expiration=1)
        testAll(c)
        print("TESTOK")


class CacheCategory():

    def __init__(self, id, db,expiration=300):
        self.id = id

        self.db = db

        if "inMem" not in db.__dict__:
            raise RuntimeError("please get db from j.servers.kvs...")

        self.expiration = expiration

    def set(self, key, value,expire=None):
        if expire==None:
            expire=self.expiration
        self.db.set(key, value, expire=expire)

    def get(self, key, method=None, refresh=False,expire=None, **kwargs):
        # check if key exists then return (only when no refresh)
        res=self.db.get(key)
        # print("res:%s"%res)
        if refresh or res == None:
            if method == None:
                raise j.exceptions.RuntimeError("Cannot get '%s' from cache,not found & method None" % key)
            # print("cache miss")
            val = method(**kwargs)
            # print(val)
            if val is None or val == "":
                raise j.exceptions.RuntimeError("cache method cannot return None or empty string.")
            self.set(key, val)
            return val
        else:
            if res == None:
                raise j.exceptions.RuntimeError("Cannot get '%s' from cache" % key)
            return res

    def reset(self):
        self.db.destroy()
