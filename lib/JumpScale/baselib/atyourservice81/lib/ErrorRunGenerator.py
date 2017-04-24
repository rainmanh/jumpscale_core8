import asyncio
from JumpScale import j
from JumpScale.baselib.atyourservice81.lib.RunScheduler import ERROR_RUN_PRIORITY

RETRY_DELAY = {
    1: 30,  # 30sec
    2: 60,  # 1min
    3: 300,  # 5min
    4: 600,  # 10min
    5: 1800,  # 30min
    6: 1800,  # 30min
}  # total: 1h 16min 30sec


class ErrorRunGenerator:
    def __init__(self, repo):
        self.logger = j.logger.get("j.ays.ErrorRunGenerator")
        self.repo = repo
        self.is_running = False

    def _actions_to_execute(self):
        """
        Walk over all servies and look for action in error states
        """
        now = j.data.time.epoch
        result = {}
        for service in self.repo.servicesFind(state='error'):
            for action, obj in service.model.actions.items():

                # only deal with job in error state
                # never schedule event actions
                if obj.state != 'error' or not obj.isJob or (action in service.model.actionsEvents):
                    continue

                # or the action is not an error, or the error is to high and we don't retry
                if obj.errorNr <= 0 or 6 < obj.errorNr:
                    continue

                # retry delay elapsed
                if (obj.lastRun + RETRY_DELAY[obj.errorNr]) <= now:
                    # add this actions to the run
                    if service not in result:
                        result[service] = list()
                    action_chain = list()
                    service._build_actions_chain(action, ds=action_chain)
                    action_chain.reverse()
                    result[service].append(action_chain)

        return result

    async def start(self):
        self.logger.info("{} started".format(self))
        if self.is_running:
            return

        self.is_running = True
        while self.is_running:
            actions_to_execute = self._actions_to_execute()

            if len(actions_to_execute) > 0:
                run = self.repo.runCreate(actions_to_execute)
                self.logger.debug("add error run {} to {}".format(run.model.key, self))
                await self.repo.run_scheduler.add(run, ERROR_RUN_PRIORITY)

            if not self.is_running:
                break
            await asyncio.sleep(30)

        self.logger.info("{} stopped".format(self))

    async def stop(self):
        self.is_running = False
        self.logger.info("{} stopping...".format(self))

    def __repr__(self):
        return "ErrorRunGenerator<{}>".format(self.repo.name)
