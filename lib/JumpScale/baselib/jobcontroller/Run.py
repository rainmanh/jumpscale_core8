from JumpScale import j

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
        return self.dbobj.state

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
            job_model = j.core.jobcontroller.db.job.get(obj.key)
            res.append(job_model.objectGet())
        return res

    def execute(self):
        processes = {}
        for job in self.jobs:
            self.logger.info('exectute %s' % job)
            process = job.execute()

            if job.model.dbobj.debug is False:
                processes[job] = process

        for job, process in processes.items():

            while not process.isDone():
                process.wait()

            service_action_obj = job.service.getActionObj(job.model.dbobj.actionName)

            if process.state != 'success':
                self.state = 'error'
                job.model.dbobj.state = 'error'
                service_action_obj.state = 'error'
                # processError creates the logs entry in job object
                job._processError(process.error)
            else:
                self.state = 'ok'
                job.model.dbobj.state = 'ok'
                service_action_obj.state = 'ok'

                log_enable = j.core.jobcontroller.db.action.get(service_action_obj.actionKey).dbobj.log
                if log_enable:
                    job.model.log(msg=process.stdout, level=5, category='out')
                    job.model.log(msg=process.stderr, level=5, category='err')

                print(process.stdout)

            job.model.save()
            job.service.model.save()

    def __repr__(self):
        out = "step:%s (%s)\n" % (self.dbobj.number, self.state)
        for job in self.jobs:
            out += "- %-25s %-25s ! %-15s %s \n" % \
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
        res = []
        for dbobj in self.model.dbobj.steps:
            step = RunStep(self, dbobj.number, dbobj=dbobj)
            res.append(step)
        return res

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
        from IPython import embed
        print("DEBUG NOW delete")
        embed()
        raise RuntimeError("stop debug here")

    def newStep(self):
        self.lastnr += 1
        dbobj = self.model.stepNew()
        step = RunStep(self, self.lastnr, dbobj=dbobj)
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

    @property
    def services(self):
        res = []
        for step in self.steps:
            res.exetend(step.services)
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
        i = len(self.steps)
        for step in self.steps:
            step.nr = i
            i -= 1
        self.steps.reverse()

    def save(self):
        self.model.save()

    def execute(self):
        self.state = 'running'

        try:
            for step in self.steps:
                step.execute()
                if step.state == 'error':
                    self.state = 'error'
                    for job in step.jobs:
                        if job.model.state == 'error':
                            log = job.model.dbobj.logs[-1]
                            job.str_error(log.log)
                    raise j.exceptions.RuntimeError("Error during execution of step %d\n See stacktrace above to identify the issue" % step.dbobj.number)

            self.state = 'ok'
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
