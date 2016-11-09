from JumpScale import j
from JumpScale.baselib.jobcontroller.Run import Run

ModelBase = j.data.capnp.getModelBaseClass()


class RunModel(ModelBase):
    """
    is state object for Run
    """

    def index(self):
        # put indexes in db as specified
        ind = "%s:%s" % (self.dbobj.state, self.dbobj.lastModDate)
        self._index.index({ind: self.key})

    def stepNew(self, **kwargs):
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

    def jobNew(self, step, **kwargs):
        olditems = [item.to_dict() for item in step.jobs]
        newlist = step.init("jobs", len(olditems) + 1)
        for i, item in enumerate(olditems):
            newlist[i] = item
        job = newlist[-1]

        for k, v in kwargs.items():
            if hasattr(job, k):
                setattr(job, k, v)

        return job

    def logNew(self, msg, **kwargs):
        olditems = [item.to_dict() for item in self.dbobj.logs]
        newlist = self.dbobj.init("logs", len(olditems) + 1)
        for i, item in enumerate(olditems):
            newlist[i] = item
        newlist[-1] = msg
        return

    def objectGet(self):
        return Run(model=self)

    # def __repr__(self):
    #     out = ""
    #     for item in self.methodslist:
    #         out += "%s\n" % item
    #     return out

    # __str__ = __repr__
