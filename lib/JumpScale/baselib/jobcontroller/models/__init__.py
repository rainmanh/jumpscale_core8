from JumpScale import j

import capnp

import model_capnp as ModelCapnp

from .JobModel import JobModel


class ModelsFactory():

    def __init__(self, aysrepo):
        self.namespacePrefix = "ays:%s" % aysrepo.name
        ModelFactory = j.data.capnp.getModelFactoryClass()

        self.capnpModel = ModelCapnp

        self.job = ModelFactory(self, "Job", JobModel)

    def destroy(self):
        self.job.destroy()
