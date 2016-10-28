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
        self.namespacePrefix = "ays:"
        self.repo = ModelFactory(self, "Repo", RepoModel, **j.atyourservice.config['redis'])
        if aysrepo:
            self.namespacePrefix = "ays:%s" % aysrepo.name
            self.actor = ModelFactory(self, "Actor", ActorModel, **j.atyourservice.config['redis'])
            self.service = ModelFactory(self, "Service", ServiceModel, **j.atyourservice.config['redis'])
            self.actor.repo = aysrepo
            self.service.repo = aysrepo

    def destroy(self):
        self.repo.destroy()
        self.actor.destroy()
        self.service.destroy()
