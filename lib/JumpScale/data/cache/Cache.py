
from JumpScale import j


class Cache:

    def __init__(self):
        self.__jslocation__ = "j.data.cache"
        self._cache = {}

    def get(self, id="main", db=None, reset=False):
        """
        @param id is a unique id for the cache
        db = e.g. j.core.db or None, when none then will be in memory
        """
        if id not in self._cache:
            self._cache[id] = CacheCategory(id=id, db=db)
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
            c.set("something", "OK")

            assert "OK" == c.get("something")

            def return1():
                return 1

            assert c.get("somethingElse", return1) == 1
            assert c.get("somethingElse") == 1

            c.reset()

            try:
                c.get("somethingElse")
            except Exception as e:
                if not "Cannot get 'somethingElse' from cache" in str(e):
                    raise RuntimeError("error in test. non expected output")

        c = self.get("test")
        testAll(c)
        c = self.get("test", j.core.db)
        testAll(c)
        print("TESTOK")


class CacheCategory():

    def __init__(self, id, db=None):
        self.id = id
        self.hkey = "cache:%s" % self.id
        self.db = db
        self._cache = {}

    def _get(self, key):
        if self.db == None:
            if key in self._cache:
                return self._cache[key]
            else:
                return None
        else:
            val = self.db.hget(self.hkey, key)
            val = j.data.serializer.json.loads(val)
            return val

    def set(self, key, val):
        if self.db == None:
            self._cache[key] = val
        else:
            val = j.data.serializer.json.dumps(val)
            self.db.hset(self.hkey, key, val)

    def get(self, key, method=None, refresh=False, **kwargs):
        if method == None and refresh == True:
            raise j.exceptions.Input(message="method cannot be None", level=1, source="", tags="", msgpub="")

        # check if key exists then return (only when no refresh)
        if refresh or self._get(key) == None:
            if method == None:
                raise j.exceptions.RuntimeError("Cannot get '%s' from cache,not found & method None" % key)
            val = method(**kwargs)
            if val is None or val == "":
                raise j.exceptions.RuntimeError("cache method cannot return None or empty string.")
            self.set(key, val)
            return val
        else:
            res = self._get(key)
            if res == None:
                raise j.exceptions.RuntimeError("Cannot get '%s' from cache" % key)
            return res

    def reset(self):
        if self.db == None:
            self._cache = {}
        else:
            self.db.delete(self.hkey)
