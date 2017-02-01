from JumpScale import j

import asyncio
import time
import pygments.lexers
from pygments.formatters import get_formatter_by_name
import colored_traceback
colored_traceback.add_hook(always=True)


class RunStep:

    def __init__(self, run, nr, dbobj):
        """
        """
        self.run = run
        self.dbobj = dbobj
        self.dbobj.number = nr
        self.logger = j.atyourservice.logger

    @property
    def state(self):
        return self.dbobj.state.__str__()

    @state.setter
    def state(self, state):
        self.dbobj.state = state

    @property
    def services(self):
        res = []
        for job in self.jobs:
            res.append(job.service)
        return res

    def addJob(self, job):
        job.model.dbobj.runKey = self.run.model.key
        job.save()

        jobobj = self.run.model.jobNew(step=self.dbobj)
        jobobj.actionName = job.model.dbobj.actionName
        jobobj.actorName = job.model.dbobj.actorName
        jobobj.key = job.model.key
        jobobj.serviceName = job.model.dbobj.serviceName
        jobobj.serviceKey = job.model.dbobj.serviceKey

    @property
    def jobs(self):
        res = []
        for obj in self.dbobj.jobs:
            job_model = j.core.jobcontroller.db.jobs.get(obj.key)
            res.append(job_model.objectGet())
        return res

    def _fake_exec(self, job):
        job.model.dbobj.state = 'ok'
        action_name = job.model.dbobj.actionName
        # if the action is a reccuring action, save last execution time in model
        if action_name in job.service.model.actionsRecurring:
            job.service.model.actionsRecurring[action_name].lastRun = j.data.time.epoch

        service_action_obj = job.service.model.actions[action_name]
        service_action_obj.state = 'ok'
        job.save()

    async def execute(self):
        futures = []
        for job in self.jobs:
            self.logger.info('execute %s' % job)
            # don't actually execute anything
            if job.service.aysrepo.no_exec is True:
                self._fake_exec(job)
            else:
                futures.append(job.execute())

        # TODO: implement timout in the asyncio.wait
        self.logger.debug("wait for all jobs to complete")
        done, pending = await asyncio.wait(futures)
        if len(pending) != 0:
            for future in pending:
                future.cancel()
            raise j.exceptions.RuntimeError('not all job done')

        states = [job.model.state for job in self.jobs]
        self.state = 'error' if 'error' in states else 'ok'
        self.logger.info("runstep {}: {}".format(self.dbobj.number, self.state))

    def __repr__(self):
        out = "step:%s (%s)\n" % (self.dbobj.number, self.state)
        for job in self.jobs:
            out += "- %-25s %-25s ! %-15s (%s)\n" % \
                (job.model.dbobj.actorName, job.model.dbobj.serviceName, job.model.dbobj.actionName, job.model.dbobj.state)
        return out

    __str__ = __repr__


class Run:

    def __init__(self, model):
        """
        """
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

        count = len(ordered)
        for i, step in enumerate(reversed(ordered)):
            self.model.dbobj.steps.adopt(i, step)
            self.model.dbobj.steps[i].number = i + 1

        self.model.save()

    def save(self):
        self.model.save()

    async def execute(self):
        """
        Execute executes all the steps contained in this run
        if a step finishes with an error state. print the error of all jobs in the step that has error states then raise any
        exeception to stop execution
        """
        self.state = 'running'
        try:
            for step in self.steps:

                await step.execute()

                if step.state == 'error':
                    self.logger.error("error during execution of step {} in run {}".format(step.dbobj.number, self.key))
                    self.state = 'error'

                    for job in step.jobs:
                        if job.model.state == 'error':
                            log = job.model.dbobj.logs[-1]
                            print(job.str_error(log.log))

                    raise j.exceptions.RuntimeError(log.log)
                    # raise j.exceptions.RuntimeError("Error during execution of step %d\n See stacktrace above to identify the issue" % step.dbobj.number)

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
