from JumpScale import j


class RunStep:

    def __init__(self, run, nr, dbobj):
        """
        """
        self.run = run
        self.nr = nr
        self.dbobj = dbobj

    @property
    def state(self):
        return self.dbobj.state

    def addJob(self, job):
        job.model.dbobj.runKey = self.run.model.key
        job.save()

        olditems = [item.to_dict() for item in self.dbobj.jobs]
        newlist = self.dbobj.init("jobs", len(olditems) + 1)
        for i, item in enumerate(olditems):
            newlist[i] = item
        jobdbobj = newlist[-1]
        jobdbobj.actionName = job.model.dbobj.actionName
        jobdbobj.actorName = job.model.dbobj.actorName
        jobdbobj.key = job.model.key
        jobdbobj.serviceName = job.model.dbobj.serviceName
        jobdbobj.serviceKey = job.model.dbobj.serviceKey
        jobdbobj.state = str(job.model.state)

    @property
    def jobs(self):
        res = []
        for obj in self.dbobj.jobs:
            res.append(j.core.jobcontroller.db.job.get(obj.key))
        return res

    def execute(self):
        # TODO: *1
        from IPython import embed
        print("DEBUG NOW implement execute on runstep")
        embed()
        raise RuntimeError("stop debug here")

    def __repr__(self):
        out = "step:%s (%s)\n" % (self.nr, self.state)
        for job in self.jobs:
            from IPython import embed
            print("DEBUG NOW repr")
            embed()
            raise RuntimeError("stop debug here")
            out += "- %-50s ! %-15s %s \n" % (service,
                                              self.action, stepaction.state)
        return out

    __str__ = __repr__


class Run:

    def __init__(self, model):
        """
        """
        self.steps = []
        self.lastnr = 0
        self.logger = j.atyourservice.logger
        self.model = model

    @property
    def state(self):
        return self.model.state

    @property
    def key(self):
        return self.model.key

    @property
    def timestamp(self):
        return self.model.epoch

    def delete(self):
        from IPython import embed
        print("DEBUG NOW delete")
        embed()
        raise RuntimeError("stop debug here")

    def newStep(self):
        self.lastnr += 1
        dbobj = self.model.stepNew()
        step = RunStep(self, self.lastnr, dbobj=dbobj)
        self.steps.append(step)
        return step

    # def sort(self):
    #     for step in self.steps:
    #         keys = []
    #         items = {}
    #         res = []
    #         for service in step.services:
    #             items[service.key] = service
    #             keys.append(service.key)
    #         keys.sort()
    #         for key in keys:
    #             res.append(items[key])
    #         step.services = res

    # @property
    # def services(self):
    #     res = []
    #     for step in self.steps:
    #         for service in step.services:
    #             res.append(service)
    #     return res
    #
    # @property
    # def action_services(self):
    #     res = []
    #     for step in self.steps:
    #         for service in step.services:
    #             res.append((step.action, service))
    #     return res

    @property
    def error(self):
        out = "%s\n" % self
        out += "***ERROR***\n\n"
        for step in self.steps:
            if step.state == "ERROR":
                for key, action in step.actions.items():
                    if action.state == "ERROR":
                        out += "STEP:%s, ACTION:%s" % (step.nr, step.action)
                        out += self.db.get_dedupe("source",
                                                  action.model["source"]).decode()
                        out += str(action.result or '')
        return out

    def reverse(self):
        i = len(self.steps)
        for step in self.steps:
            step.nr = i
            i -= 1
        self.steps.reverse()

    def save(self):
        if self.db is not None:
            # will remember in KVS
            self.db.set("run %s" % str(self.id),
                        j.data.serializer.json.dumps(self.model))
            self.db.set("run_index %s" % str(self.id), "%s|%s" %
                        (self.timestamp, self.state))

    def execute(self):
        # j.actions.setRunId("ays_run_%s"%self.id)
        for step in self.steps:
            step.execute()
            if self.state == "ERROR":
                # means there was error in this run, then we need to stop
                self.save()
                raise j.exceptions.RuntimeError(self.error)
        self.state = "OK"
        self.save()

    def __repr__(self):
        out = "RUN:%s\n" % (self.key)
        out += "-------\n"
        for step in self.steps:
            out += "## step:%s\n\n" % step.nr
            out += "%s\n" % step
        return out

    __str__ = __repr__
