
from JumpScale import j
# import ExtraTools


class Cache:

    def __init__(self):
        self.__jslocation__ = "j.data.cache"
        self.db = j.core.db
        self._cache = {}

    def get(self, runid, cat, keepInMem=False, reset=False):
        if self.db == None:
            keepInMem = True
        key = "%s_%s" % (runid, cat)
        if key not in self._cache:
            self._cache[key] = CacheCategory(runid, cat, keepInMem=keepInMem)
        if reset:
            self.reset(runid)
        return self._cache[key]

    def reset(self, runid=""):
        if self.db != None:
            self._cache = {}
            if runid == "":
                for key in j.core.db.keys():
                    key = key.decode()
                    if key.startswith("cuisine:cache"):
                        print("cache delete:%s" % key)
                        j.core.db.delete(key)
            else:
                key = "cuisine.cache.%s" % runid
                j.core.db.delete(key)


class CacheCategory():

    def __init__(self, runid, cat, keepInMem=False):
        self.cat = cat
        self.runid = runid
        self.keepInMem = keepInMem
        if keepInMem:
            self._cache = {}

    def get(self, id, method=None, refresh=False, **kwargs):
        key = "cuisine:cache:%s" % self.runid
        hkey = "%s:%s" % (self.cat, id)
        if self.keepInMem and id in self._cache and refresh is False:
            if self._cache[id] not in ["", None]:
                return self._cache[id]
        if refresh is False and j.core.db != None:
            val = j.core.db.hget(key, hkey)
            if val is not None:
                val = j.data.serializer.json.loads(val)
                if val is not None and val != "":
                    return val
        if method is not None:
            val = method(**kwargs)
            if val is None or val == "":
                raise j.exceptions.RuntimeError("method cannot return None or empty string.")
            self.set(id, val)
            if self.keepInMem:
                self._cache[id] = val
            return val
        raise j.exceptions.RuntimeError("Cannot get '%s' from cache" % id)

    def set(self, id, val):
        self._cache[id] = val
        if j.core.db != None:
            key = "cuisine:cache:%s" % self.runid
            hkey = "%s:%s" % (self.cat, id)
            val = j.data.serializer.json.dumps(val)
            j.core.db.hset(key, hkey, val)

    def reset(self):
        j.data.cache.reset(self.runid)
        if self.keepInMem:
            self._cache = {}
