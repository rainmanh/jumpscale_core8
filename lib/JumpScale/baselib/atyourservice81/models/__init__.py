from JumpScale import j

import capnp
import model_capnp as ModelCapnp

from .ActorModel import ActorModel
from .ServiceModel import ServiceModel


class ModelsFactory():

    def __init__(self, aysrepo):
        self.namespacePrefix = "ays:%s" % aysrepo.name
        ModelFactory = j.data.capnp.getModelFactoryClass()
        self.capnpModel = ModelCapnp

        self.actor = ModelFactory(self, "Actor", ActorModel)
        self.service = ModelFactory(self, "Service", ServiceModel)

        self.actor.repo = aysrepo
        self.service.repo = aysrepo

    def destroy(self):
        self.actor.destroy()
        self.service.destroy()
