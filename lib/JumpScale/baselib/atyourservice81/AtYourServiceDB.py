
from JumpScale import j

# import capnp
import re
import aysmodel_capnp as AYSModel

from JumpScale.baselib.atyourservice81.models import ActorModel, JobModel, RunModel, ServiceModel, ActionCodeModel


class AtYourServiceDBFactory():

    def __init__(self):
        self.AYSModel = AYSModel
        self.actor = ModelFactory("Actor")
        self.job = ModelFactory("Job")
        self.actionCode = ModelFactory("ActionCode")
        self.service = ModelFactory("Service")
        self.run = ModelFactory("Run")
        self.db = AtYourServiceDB()
        self.dbIndex = AtYourServiceDB()


class ModelFactory():

    def __init__(self, category):
        self.category = category
        self._db = AtYourServiceDB(category=category)  # is the abstraction layer to low level db
        self._index = AtYourServiceDB(category="index_%s" % category)
        self._modelClass = eval(self.category + "Model." + self.category + "Model")
        self.list = self._modelClass.list
        self.find = self._modelClass.find

    def new(self):
        model = self._modelClass(category=self.category, db=self._db, index=self._index)
        return model

    def get(self, key):
        model = self._modelClass(category=self.category, db=self._db, index=self._index, key=key)
        return model

    def delete(self, key):
        self._db.delete(key=key)

    def destroy(self):
        self._db.destroy()

    def exists(self, key):
        return self._db.exists(key=key)


class AtYourServiceDB():

    def __init__(self, db=None):
        if db == None:
            self.db = j.servers.kvs.getRedisStore("ays", changelog=False)
        else:
            self.db = db

    def set(self, obj):
        """
        obj key & secret needs to be given, secret allows modification if there is distinction between key & secret
        """
        self.db.set(self.category, key, obj)

    def get(self, key):
        return self.db.get(self.category, key)

    def delete(self, key):
        self.db.delete(self.category, key)

    def increment(self, key):
        return self.db.increment(key)

    def destroy(self):
        self.db.destroy()

    def exists(self, key):
        return self.db.exists(self.category, key)

    def getQueue(self, queue):
        return self.db.redisclient.getQueue(queue)

    def index(self, items):
        """
        items is {indexitem:key}
        indexitem is e.g. $actorname:$state:$role (is a text which will be index to key)
        indexitems are always made lowercase
        ':' is not allowed in indexitem
        """
        # if in non redis, implement as e.g. str index in 1 key and if gets too big then create multiple
        for key, val in items.items():
            self.db.redisclient.hset("index", key.lower(), val)
        return True

    def list(self, regex=".*", returnIndex=False):
        """
        regex is regex on the index, will return matched keys
        e.g. .*:new:.* would match all actors with state new
        """
        res = []
        for item in self.db.redisclient.hkeys("index"):
            item = item.decode()
            if re.match(regex, item) is not None:
                key = self.db.redisclient.hget("index", item).decode()
                if returnIndex == False:
                    res.append(key)
                else:
                    res.append((item, key))
        return res
