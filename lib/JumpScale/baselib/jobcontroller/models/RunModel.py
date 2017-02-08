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

    def stepNew(self):
        step = j.data.capnp.getMemoryObj(self._capnp_schema.RunStep)
        self.dbobj.steps.append(step)
        return step

    def jobNew(self, step):
        job = j.data.capnp.getMemoryObj(self._capnp_schema.Job)
        step.jobs.append(job)
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

    def delete(self):
        ind = "%s:%s" % (self.dbobj.state, self.dbobj.lastModDate)
        self._index.index_remove(ind)
        # delete actual model object
        if self._db.exists(self.key):
            self._db.delete(self.key)

    def objectGet(self):
        return Run(model=self)

    # def __repr__(self):
    #     out = ""
    #     for item in self.methodslist:
    #         out += "%s\n" % item
    #     return out

    # __str__ = __repr__
