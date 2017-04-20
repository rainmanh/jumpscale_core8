import colored_traceback
from JumpScale.baselib.jobcontroller.RunStep import RunStep
from JumpScale import j

colored_traceback.add_hook(always=True)


class Run:

    def __init__(self, model):
        self.lastnr = 0
        self.logger = j.atyourservice.logger
        self.model = model

    @property
    def steps(self):
        steps = []
        for dbobj in self.model.dbobj.steps:
            step = RunStep(self, dbobj.number, dbobj=dbobj)
            steps.append(step)
        return steps

    @property
    def state(self):
        return self.model.dbobj.state

    @state.setter
    def state(self, state):
        self.model.dbobj.state = state

    @property
    def key(self):
        return self.model.key

    @property
    def timestamp(self):
        return self.model.epoch

    def delete(self):
        self.model.delete()

    def newStep(self):
        self.lastnr += 1
        dbobj = self.model.stepNew()
        step = RunStep(self, self.lastnr, dbobj=dbobj)
        return step

    @property
    def services(self):
        res = []
        for step in self.steps:
            res.extend(step.services)
        return res

    def hasServiceForAction(self, service, action):
        for step in self.steps:
            for job in step.jobs:
                if job.model.dbobj.actionName != action:
                    continue
                if job.service == service:
                    return True
        return False

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
        ordered = []
        for i, _ in enumerate(self.model.dbobj.steps):
            orphan = self.model.dbobj.steps.disown(i)
            ordered.append(orphan)

        for i, step in enumerate(reversed(ordered)):
            self.model.dbobj.steps.adopt(i, step)
            self.model.dbobj.steps[i].number = i + 1

        self.model.save()

    def save(self):
        self.model.save()

    async def execute(self):
        """
        Execute executes all the steps contained in this run
        if a step finishes with an error state.
        print the error of all jobs in the step that has error states then raise any
        exeception to stop execution
        """
        self.state = 'running'
        try:
            for step in self.steps:

                await step.execute()

                if step.state == 'error':
                    self.logger.error("error during execution of step {} in run {}".format(step.dbobj.number, self.key))
                    self.state = 'error'
                    err_msg = ''
                    for job in step.jobs:
                        if job.model.state == 'error':
                            if len(job.model.dbobj.logs) > 0:
                                log = job.model.dbobj.logs[-1]
                                print(job.str_error(log.log))
                                err_msg = log.log

                    raise j.exceptions.RuntimeError(err_msg)

            self.state = 'ok'
        except:
            self.state = 'error'
            raise
        finally:
            self.save()

    def __repr__(self):
        out = "RUN:%s\n" % (self.key)
        out += "-------\n"
        for step in self.steps:
            out += "## step:%s\n\n" % step.dbobj.number
            out += "%s\n" % step
        return out

    __str__ = __repr__
