
from JumpScale import j

import capnp
import aysmodel_capnp as AYSModel

from ActorModel import ActorModel
from JobModel import JobModel


class AtYourServiceDBFactory():

    def __init__(self):
        self.AYSModel = AYSModel
        self.actor = ModelFactory("Actor")
        self.job = ModelFactory("Job")
        # self.service = ModelFactory("Service")
        # self.actioncode = ModelFactory("ActionCode")
        # self.run = ModelFactory("Run")

    def getDB(self, category):
        return AtYourServiceDB(category)


class ModelFactory():

    def __init__(self, category):
        self.category = category
        self._db = AtYourServiceDB(category=category)  # is the abstraction layer to low level db
        self._modelClass = eval(self.category + "Model")

    def new(self):
        model = self._modelClass(self.category, self._db)
        return model

    def get(self, key):
        model = self._modelClass(self.category, self._db, key=key)
        return model

    def delete(self, key):
        self._db.delete(self.category, key)

    def destroy(self):
        self._db.destroy()

    def exists(self, key):
        return self._db.exists(self.category, key)


class AtYourServiceDB():

    def __init__(self, category):
        self.category = category
        self.db = j.servers.kvs.getRedisStore("ays", changelog=False)

    def set(self, key, obj):
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

    def hset(self, name, key, value):
        # is not compatible with other kvs's. Not good. Rethink
        self.db.redisclient.hset(name, key, value)
        return True

    def hget(self, name, key):
        # is not compatible with other kvs's. Not good. Rethink
        return self.db.redisclient.hget(name, key)
