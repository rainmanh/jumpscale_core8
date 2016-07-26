
from JumpScale import j
# import ExtraTools


class Cache:

    def __init__(self):
        self.__jslocation__ = "j.data.cache"
        self.db=j.core.db
        self.memcache={}

    def get(self,runid,cat,keepInMem=False,reset=False):
        key="%s_%s"%(runid,cat)
        if key not in self.memcache:
            self.memcache[key]=CacheCategory(runid,cat,keepInMem=keepInMem)
        if reset:
            self.reset(runid)
        return self.memcache[key]

    def reset(self,runid=""):
        if runid=="":
            for key in j.core.db.keys():
                key=key.decode()
                if key.startswith("cuisine:cache"):
                    print ("cache delete:%s"%key)
                    j.core.db.delete(key)
        else:
            key="cuisine.cache.%s"%runid
            j.core.db.delete(key)


class CacheCategory():

    def __init__(self,runid,cat,keepInMem=False):
        self.cat=cat
        self.runid=runid
        self.keepInMem=keepInMem
        if keepInMem:
            self.memcache={}

    def get(self,id,method=None,refresh=False,**kwargs):
        key="cuisine:cache:%s"%self.runid
        hkey="%s:%s"%(self.cat,id)
        if self.keepInMem and id in self.memcache and refresh==False:
            return self.memcache[id]
        val=j.core.db.hget(key,hkey)
        if val!=None and refresh==False:
            val=j.data.serializer.json.loads(val)
            return val
        if method!=None:
            val=method(**kwargs)
            if val==None:
                raise j.exceptions.RuntimeError("method cannot return None")
            self.set(id,val)
            if self.keepInMem:
                self.memcache[id]=val
            return val
        raise j.exceptions.RuntimeError("Cannot get '%s' from cache"%id)

    def set(self,id,val):
        key="cuisine:cache:%s"%self.runid
        hkey="%s:%s"%(self.cat,id)
        val=j.data.serializer.json.dumps(val)
        j.core.db.hset(key,hkey,val)

    def reset(self):
        j.data.cache.reset(self.runid)
        if keepInMem:
            self.memcache={}        


