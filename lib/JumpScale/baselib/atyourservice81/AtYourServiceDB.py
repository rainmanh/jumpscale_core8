
from JumpScale import j

# import capnp
import re
import aysmodel_capnp as AYSModel

from JumpScale.baselib.atyourservice81.models import ActorModel, JobModel, RunModel, ServiceModel, ActionCodeModel


class AtYourServiceDBFactory():

    def __init__(self, repo):
        self.repo = repo
        self.AYSModel = AYSModel
        self.actor = ModelFactory("Actor", repo)
        self.job = ModelFactory("Job", repo)
        self.actionCode = ModelFactory("ActionCode", repo)
        self.service = ModelFactory("Service", repo)
        self.run = ModelFactory("Run", repo)

    def destroy(self):
        self.actor.destroy()
        self.job.destroy()
        self.actionCode.destroy()
        self.service.destroy()
        self.run.destroy()


class ModelFactory():

    def __init__(self, category, repo):
        self.category = category
        self.repo = repo
        reponame = self.repo.name
        self._db = j.servers.kvs.getRedisStore("ays:%s:%s" % (reponame, category), changelog=False)
        self._index = j.servers.kvs.getRedisStore("ays:%s:%s" % (reponame, category), changelog=False)
        self._modelClass = eval(self.category + "Model." + self.category + "Model")
        self._capnp = eval("AYSModel." + self.category)
        self.list = self._modelClass.list
        self.find = self._modelClass.find

        self.exists = self._db.exists
        self.queueSize = self._db.queueSize
        self.queuePut = self._db.queuePut
        self.queueGet = self._db.queueGet
        self.queueFetch = self._db.queueFetch

    def new(self):
        model = self._modelClass(modelfactory=self)
        return model

    def get(self, key):
        model = self._modelClass(modelfactory=self, key=key)
        return model

    def destroy(self):
        self._db.destroy()
        self._index.destroy()
