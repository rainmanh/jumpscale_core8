from JumpScale import j

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
            job_model = j.core.jobcontroller.db.jobs.get(obj.key)
            res.append(job_model.objectGet())
        return res

    def execute(self):
        processes = {}
        for job in self.jobs:
            self.logger.info('execute %s' % job)
            process = job.execute()

            if job.model.dbobj.debug is False:
                now = j.data.time.epoch
                processes[job] = {'process': process, 'epoch': j.data.time.epoch}

        # loop over all jobs from a step, waiting for them to be done
        # printing output of the jobs as it get synced from the subprocess
        all_done = False
        last_output = None
        while not all_done:
            all_done = True

            for job, process_info in processes.items():
                process = process_info['process']

                if not process.isDone():
                    all_done = False
                    time.sleep(0.5)
                    process.sync()

                    if process.new_stdout != "":
                        if last_output != job.model.key:
                            self.logger.info("stdout of %s" % job)
                        self.logger.info(process.new_stdout)
                        last_output = job.model.key

        # save state of jobs, process logs and errors
        for job, process_info in processes.items():
            process = process_info['process']
            action_name = job.model.dbobj.actionName

            while not process.isDone():
                self.logger.debug('wait for {}'.format(str(job)))
                # just to make sure process is cleared
                process.wait()

            # if the action is a reccuring action, save last execution time in model
            if action_name in job.service.model.actionsRecurring:
                job.service.model.actionsRecurring[action_name].lastRun = process_info['epoch']

            service_action_obj = job.service.model.actions[action_name]

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

                log_enable = j.core.jobcontroller.db.actions.get(service_action_obj.actionKey).dbobj.log
                if log_enable:
                    if process.stdout != '':
                        job.model.log(msg=process.stdout, level=5, category='out')
                    if process.stderr != '':
                        job.model.log(msg=process.stderr, level=5, category='err')
                self.logger.info("job {} done sucessfuly".format(str(job)))

            job.save()

    def __repr__(self):
        out = "step:%s (%s)\n" % (self.dbobj.number, self.state)
        for job in self.jobs:
            out += "- %-25s %-25s ! %-15s\n" % \
                (job.model.dbobj.actorName, job.model.dbobj.serviceName, job.model.dbobj.actionName)
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
        from IPython import embed
        print("DEBUG NOW delete")
        embed()
        raise RuntimeError("stop debug here")

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

    def execute(self):
        """
        Execute executes all the steps contained in this run
        if a step finishes with an error state. print the error of all jobs in the step that has error states then raise any
        exeception to stop execution
        """
        self.state = 'running'
        try:
            for step in self.steps:

                step.execute()

                if step.state == 'error':
                    self.state = 'error'

                    for job in step.jobs:
                        if job.model.state == 'error':
                            log = job.model.dbobj.logs[-1]
                            print(job.str_error(log.log))

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
