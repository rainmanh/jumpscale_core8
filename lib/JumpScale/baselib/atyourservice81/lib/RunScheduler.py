import asyncio
from JumpScale import j

NORMAL_RUN_PRIORITY = 1
ERROR_RUN_PRIORITY = 10

RETRY_DELAY = {
    1: 10,  # 30sec
    2: 60,  # 1min
    3: 300,  # 5min
    4: 600,  # 10min
    5: 1800,  # 30min
    6: 1800,  # 30min
}  # total: 1h 16min 30sec


class RunScheduler:
    """
    This class is reponsible to execte the run requested by the users
    as well as the automatic error runs

    Since only one can be executed at a time, all the run are pushed on a PriorityQueue.
    Requested runs have always hightest priority over error runs.
    """

    def __init__(self, repo):
        self.logger = j.logger.get("j.ays.RunScheduler")
        self.repo = repo
        self.queue = asyncio.PriorityQueue(maxsize=0)
        self.is_running = False

    async def start(self):
        self.logger.info("{} started".format(self))
        if self.is_running:
            return

        self.is_running = True
        while self.is_running:
            _, run = await self.queue.get()
            if not self.is_running:
                break

            try:
                await run.execute()
            except:
                # exception is handle in the job directly,
                # catch here to not interrupt the loop
                pass
            finally:
                self.queue.task_done()

        self.logger.info("{} stopped".format(self))

    async def stop(self, timeout=30):
        self.is_running = False
        self.logger.info("{} stopping...".format(self))

        try:
            await asyncio.wait_for(self.queue.join(), timeout=timeout, loop=self.repo._loop)
        except asyncio.TimeoutError:
            self.logger.warning("stop timeout reach for {}. possible run interrupted".format(self))

    async def add(self, run, prio=NORMAL_RUN_PRIORITY):
        """
        add a run to the queue of run to be executed
        """
        if not self.is_running:
            raise j.exceptions.RuntimeError("Trying to add a run to a stopped run scheduler ({})".format(self))

        self.logger.debug("add run {} to {}".format(run.model.key, self))
        await self.queue.put((prio, run))

    async def retry(self, job):
        """
        TODO
        """
        action_name = job.model.dbobj.actionName
        action = job.service.model.actions[action_name]

        if action.state != 'error':
            self.logger.info("no need to retry action {}, state not error".format(action))
            return

        if list(RETRY_DELAY.keys())[-1] < action.errorNr:
            self.logger.info("action {} reached max retry, not rescheduling again.".format(action))
            return

        delay = RETRY_DELAY[action.errorNr]
        # make sure we don't reschedule with a delay smaller then the timeout of the job
        if action.timeout > 0:
            delay + action.timeout
        self.logger.info("reschedule {} in {}sec".format(job, delay))
        await asyncio.sleep(delay)

        run = self.repo.runCreate({job.service: [[action_name]]})
        self.logger.debug("add error run {} to {}".format(run.model.key, self))
        await self.repo.run_scheduler.add(run, ERROR_RUN_PRIORITY)

    def __repr__(self):
        return "RunScheduler<{}>".format(self.repo.name)
