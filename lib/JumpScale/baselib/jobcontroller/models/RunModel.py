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
        idx_list = self._index.list(returnIndex=True)
        matched_idx = [item for item in idx_list if item[1] == self.key]
        if matched_idx:
            #  if the key exists first pop it and add the correct one
            item = matched_idx[0]
            self._index.redisclient.hdel(self._index._indexkey, item[0])
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

    @property
    def logs(self):
        logs = list()
        steps = [item.to_dict() for item in self.dbobj.steps]
        steps_with_errors = [step for step in steps if step['state'] == 'error']
        jobs = [job for step in steps_with_errors for job in step['jobs']]
        for job in jobs:
            job_model = j.core.jobcontroller.db.jobs.get(job['key'])
            logs.extend(job_model.dictFiltered['logs'])

        return logs


    def objectGet(self):
        return Run(model=self)

    # def __repr__(self):
    #     out = ""
    #     for item in self.methodslist:
    #         out += "%s\n" % item
    #     return out

    # __str__ = __repr__
