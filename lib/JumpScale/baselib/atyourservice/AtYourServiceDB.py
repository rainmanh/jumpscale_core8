
from JumpScale import j

import capnp
import aysmodel_capnp as AYSModel

from JumpScale.baselib.atyourservice.models import ActorModel, JobModel, RunModel, ServiceModel, ActionCodeModel


class AtYourServiceDBFactory():

    def __init__(self):
        self.AYSModel = AYSModel
        self.actor = ModelFactory("Actor")
        self.job = ModelFactory("Job")
        self.actionCode = ModelFactory("ActionCode")
        self.service = ModelFactory("Service")
        self.run = ModelFactory("Run")

    def getDB(self, category):
        return AtYourServiceDB(category)


class ModelFactory():

    def __init__(self, category):
        self.category = category
        self._db = AtYourServiceDB(category=category)  # is the abstraction layer to low level db
        self._modelClass = eval(self.category + "Model." + self.category + "Model")

    def new(self):
        model = self._modelClass(category=self.category, db=self._db)
        return model

    def get(self, key):
        model = self._modelClass(category=self.category, db=self._db, key=key)
        return model

    def delete(self, key):
        self._db.delete(key=key)

    def destroy(self):
        self._db.destroy()

    def exists(self, key):
        return self._db.exists(key=key)


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
