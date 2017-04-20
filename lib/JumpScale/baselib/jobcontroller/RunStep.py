import asyncio
from JumpScale import j


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
        return [job.service for job in self.jobs]

    @property
    def jobs(self):
        res = []
        for obj in self.dbobj.jobs:
            job_model = j.core.jobcontroller.db.jobs.get(obj.key)
            if job_model:
                res.append(job_model.objectGet())
            else:
                j.logger.log('No job found with key [%s]' % obj.key)
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

        async def enhanced_waiter(future, timeout, job):
            try:
                if timeout == 0:
                    timeout = 3000
                await asyncio.wait_for(future, timeout)
            except asyncio.TimeoutError as e:
                job.state = 'error'
                self.logger.error(e)

        futures = []
        for job in self.jobs:
            action_name = job.model.dbobj.actionName
            service = job.service
            action_timeout = service.model.actions[action_name].timeout
            self.logger.info('execute %s' % job)
            # don't actually execute anything
            if job.service.aysrepo.no_exec is True:
                self._fake_exec(job)
            else:
                future = asyncio.ensure_future(enhanced_waiter(job.execute(), action_timeout, job))
                futures.append(future)

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
