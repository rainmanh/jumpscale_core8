from JumpScale import j

import capnp

import model_capnp as ModelCapnp

from .JobModel import JobModel
from .ActionModel import ActionModel


class ModelsFactory():

    def __init__(self, aysrepo):
        self.namespacePrefix = "jobs"
        ModelFactory = j.data.capnp.getModelFactoryClass()

        self.capnpModel = ModelCapnp

        self.job = ModelFactory(self, "Job", JobModel)
        self.action = ModelFactory(self, "Action", ActionModel)

    def destroy(self):
        self.job.destroy()
        self.action.destroy()
