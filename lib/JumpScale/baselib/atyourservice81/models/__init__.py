from JumpScale import j

import capnp

import model_capnp as ModelCapnp

from .ActorModel import ActorModel
from .RunModel import RunModel
from .ServiceModel import ServiceModel
from .ActionCodeModel import ActionCodeModel

# JobModel


class ModelsFactory():

    def __init__(self, aysrepo):
        self.namespacePrefix = "ays:%s" % aysrepo.name
        ModelFactory = j.data.capnp.getModelFactoryClass()
        self.capnpModel = ModelCapnp
        self.actor = ModelFactory(self, "Actor", ActorModel)
        # self.job = ModelFactory(namespacePrefix, "Job")
        self.actionCode = ModelFactory(self, "ActionCode", ActionCodeModel)
        self.service = ModelFactory(self, "Service", ServiceModel)
        self.run = ModelFactory(self, "Run", RunModel)

        self.actor.repo = aysrepo
        self.service.repo = aysrepo
        self.run.repo = aysrepo
        self.actionCode.repo = aysrepo

    def destroy(self):
        self.actor.destroy()
        # self.job.destroy()
        self.actionCode.destroy()
        self.service.destroy()
        self.run.destroy()
