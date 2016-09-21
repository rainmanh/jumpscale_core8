from JumpScale import j

import capnp

import model_job_capnp as ModelCapnp

from .JobModel import JobModel
from .ActionModel import ActionModel
from .RunModel import RunModel


class ModelsFactory():

    def __init__(self, aysrepo):
        self.namespacePrefix = "jobs"
        ModelFactory = j.data.capnp.getModelFactoryClass()

        self.capnpModel = ModelCapnp

        self.job = ModelFactory(self, "Job", JobModel)
        self.action = ModelFactory(self, "Action", ActionModel)
        self.run = ModelFactory(self, "Run", RunModel)

    def destroy(self):
        self.job.destroy()
        self.action.destroy()
        self.run.destroy()
