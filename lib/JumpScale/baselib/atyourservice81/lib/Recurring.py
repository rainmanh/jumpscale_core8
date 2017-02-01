from JumpScale import j
import asyncio

class RecurringTask:
    """Execute a job periodicly"""
    def __init__(self, service, action, period, loop=None):
        self._loop = None or asyncio.get_event_loop()
        self._future = None
        self.service = service
        self.action = action
        self.period = period
        self.started = False

    async def _run(self):
        while self.started:
            await self.service.executeActionJob(actionName=self.action)
            action_info = self.service.model.actions[self.action]
            elapsed = (j.data.time.epoch - action_info.lastRun)
            sleep = action_info.period - elapsed
            if sleep < 0:
                sleep = 0
            await asyncio.sleep(sleep)

    def start(self):
        self.started = True
        self._future = asyncio.ensure_future(self._run(), loop=self._loop)

    def stop(self):
        if self._future and not self._future.done():
            self.started = False
            self._future.cancel()


if __name__ == '__main__':
    import logging
    logging.basicConfig()

    loop = asyncio.get_event_loop()

    j.atyourservice.aysRepos._load()
    repo = j.atyourservice.aysRepos.get('/opt/code/cockpit_repos/testrepo')
    s = repo.serviceGet('node','demo')
    t = RecurringTask(s,'monitor', 10, loop=loop)
    t.start()
    def cb(t):
        t.stop()
    loop.call_later(20, cb, t)
    loop.run_forever()

    from IPython import embed;embed()
