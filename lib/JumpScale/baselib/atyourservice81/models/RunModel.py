from JumpScale import j

ModelBase = j.data.capnp.getModelBaseClass()


class RunModel(ModelBase):
    """
    is state object for Run
    """

    @classmethod
    def list(self, state="", fromEpoch=0, toEpoch=999999999, returnIndex=False):
        if state == "":
            state = ".*"
        epoch = ".*"
        regex = "%s:%s" % (state, epoch)
        res0 = j.atyourservice.db.job._index.list(regex, returnIndex=True)
        res1 = []
        for index, key in res0:
            epoch = int(index.split(":")[-1])
            if fromEpoch < epoch and epoch < toEpoch:
                if returnIndex:
                    res1.append((index, key))
                else:
                    res1.append(key)
        return res1

    def index(self):
        # put indexes in db as specified
        ind = "%s:%s" % (self.dbobj.state,  self.dbobj.lastModDate)
        self._index.index({ind: self.key})

    @classmethod
    def find(self, state="", fromEpoch=0, toEpoch=999999999):
        res = []
        for key in self.list(state, fromEpoch, toEpoch):
            res.append(self._modelfactory.get(key))
        return res

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

    # def __repr__(self):
    #     out = ""
    #     for item in self.methodslist:
    #         out += "%s\n" % item
    #     return out

    # __str__ = __repr__
