
from JumpScale import j

# import capnp
import re
import aysmodel_capnp as AYSModel

from JumpScale.baselib.atyourservice81.models import ActorModel, JobModel, RunModel, ServiceModel, ActionCodeModel

from IPython import embed
print("DEBUG NOW load ServiceModel")
embed()
raise RuntimeError("stop debug here")


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
        ns = "ays:%s:%s" % (reponame, category)
        self._db = j.servers.kvs.getRedisStore(ns, ns, changelog=False)
        # for now we do index same as database
        self._index = j.servers.kvs.getRedisStore(ns, ns, changelog=False)
        self._modelClass = eval(self.category + "Model." + self.category + "Model")
        self._capnp = eval("AYSModel." + self.category)
        self.list = self._modelClass.list
        self.find = self._modelClass.find

        # on class level we need relation to _index & _modelfactory
        self._modelClass._index = self._index
        self._modelClass._modelfactory = self

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

    def __str__(self):
        return("modelfactory:%s:%s" % (self.repo.name, self.category))

    __repr__ = __str__
