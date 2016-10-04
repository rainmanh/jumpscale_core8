from JumpScale import j

import capnp
import model_capnp as ModelCapnp

from .ActorModel import ActorModel
from .ServiceModel import ServiceModel
from .RepoModel import RepoModel


class ModelsFactory():

    def __init__(self, aysrepo=None):
        ModelFactory = j.data.capnp.getModelFactoryClass()
        self.capnpModel = ModelCapnp
        if not aysrepo:
            self.namespacePrefix = "ays:"
            self.repo = ModelFactory(self, "Repo", RepoModel)
        else:
            self.namespacePrefix = "ays:%s" % aysrepo.name

            self.actor = ModelFactory(self, "Actor", ActorModel)
            self.service = ModelFactory(self, "Service", ServiceModel)

            self.actor.repo = aysrepo
            self.service.repo = aysrepo

    def destroy(self):
        self.actor.destroy()
        self.service.destroy()
