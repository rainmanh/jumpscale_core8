from JumpScale import j

from .ModelBase import ModelBase


class RunModel(ModelBase):
    """
    is state object for Run
    """

    def __init__(self, category, db, key=""):
        self._capnp = j.atyourservice.db.AYSModel.Run
        ModelBase.__init__(self, category, db, key)

    def step_new(self, **kwargs):
        olditems = [item.to_dict() for item in self.dbobj.steps]
        newlist = self.dbobj.init("steps", len(olditems) + 1)
        for i, item in enumerate(olditems):
            newlist[i] = item
        step = newlist[-1]

        for k, v in kwargs.items():
            if k == 'jobs':
                for job in v:
                    self.job_new(step, job.to_dict())
            if hasattr(step, k):
                setattr(step, k, v)

        return step

    def job_new(self, step, **kwargs):
        olditems = [item.to_dict() for item in step.jobs]
        newlist = step.init("jobs", len(olditems) + 1)
        for i, item in enumerate(olditems):
            newlist[i] = item
        job = newlist[-1]

        for k, v in kwargs.items():
            if hasattr(job, k):
                setattr(job, k, v)

        return job

    def runSteps(self):
        olditems = [item.to_dict() for item in self.dbobj.stateChanges]
        newlist = self.dbobj.init("stateChanges", len(olditems) + 1)
        for i, item in enumerate(olditems):
            newlist[i] = item
        return newlist[-1]


    def _pre_save(self):
        # need to call finish on DynamicResizableListBuilder to prevent leaks
        for builder in [self.dbobj.steps]:
            if builder is not None:
                builder.finish()

    def _get_key(self):
        if self.dbobj.name == "":
            raise j.exceptions.Input(message="name cannot be empty", level=1, source="", tags="", msgpub="")
        return self.dbobj.name

    # def __repr__(self):
    #     out = ""
    #     for item in self.methodslist:
    #         out += "%s\n" % item
    #     return out

    # __str__ = __repr__
