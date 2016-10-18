from JumpScale import j
import signal
import time
from multiprocessing import Pool
from threading import Thread

defaultConfig = {
    'redis': {
        'unixsocket': '/tmp/ays.sock'
    }
}


def run_action(request):
    action = request['action']
    args = request.get('args', {})
    repo = j.atyourservice.repoGet(request['repo_path'])
    service = repo.db.service.get(request['service_key']).objectGet(repo)
    service.runAction(action, args)


class Server:
    """AtYourService server"""

    def __init__(self, config_path=None):
        if config_path is None:
            self._config_path = j.sal.fs.joinPaths(j.dirs.cfgDir, 'ays/ays.conf')
        else:
            self._config_path = config_path
        self._config = self._load_config(self._config_path)

        self._command_queue = j.servers.kvs.getRedisStore("ays_server", namespace='db', **self._config['redis'])

        self.logger = j.atyourservice.logger

        self._recurring_loop = RecurringLoop()
        self._workers = Pool()

        # self._set_signale_handler()

        self._running = False

    def _load_config(self, path):
        if not j.sal.fs.exists(path):
            return defaultConfig

        cfg = j.data.serializer.toml.load(path)
        if 'redis' not in cfg:
            return defaultConfig

        return cfg

    def _set_signale_handler(self):
        def stop(signum, stack_frame):
            self.stop()

        signal.signal(signal.SIGINT, stop)

    def start(self):
        if self._running is True:
            return

        self._recurring_loop.start()

        self.logger.info('starting server')
        self._running = True

        while self._running:
            payload = self._command_queue.queueGet('command', timeout=2)
            if payload is None:
                # timeout without receiving command
                continue

            try:
                request = j.data.serializer.json.loads(payload.decode())
            except Exception as e:
                self.logger.error("can't deserialize payload : %s" % str(e))
                continue

            if not j.data.types.dict.check(request) or 'command' not in request:
                self.logger.error("request doesn't have proper format, should be a dict with a 'command' key. request is: %s" % request)
                continue

            self._dispatch(request)

        self.logger.info('server stopped')

    def stop(self):
        if self._recurring_loop.is_alive():
            self.logger.info("stopping monitor recurring process")
            self._recurring_loop.stop()
            # FIXME: why:  assert self._parent_pid == os.getpid(), 'can only join a child process'
            # self._recurring_loop.join()

        if self._running:
            self._running = False
            self.logger.info("stopping server")

        self.logger.info("wait for all jobs to finish")
        self._workers.close()
        self._workers.join()

    def _dispatch(self, request):
        self.logger.info('dispatch request %s' % request)

        # TODO: implement other commands
        if request['command'] == 'execute':
            self._execute(request)

        elif request['command'] == 'event':
            self._progagate_event(request)

    def _execute(self, request):
        if 'action' not in request:
            self.logger.error('execute command received but not action specified in request.')
            return

        try:
            self._workers.apply_async(run_action, (request,))
        except Exception as e:
            self.logger.error('error: %s' % str(e))

    def _progagate_event(self, request):
        if 'event' not in request:
            self.logger.error('event command received but not event type specified in request.')
            return

        event_type = request['event']
        args = request.get('args', {})

        for repo in j.atyourservice.reposList():
            for service in repo.services:
                if len(service.model.actionsEvent) <= 0:
                    continue

                for action_name, event_obj in service.model.actionsEvent.items():
                    if event_obj.event != event_type:
                        continue

                    self.logger.info('event %s propagated to %s from %s' % (event_type, service, repo))

                    event_obj.lastRun = j.data.time.epoch
                    service.save()

                    request = {
                        'repo_path': service.aysrepo.path,
                        'service_key': service.model.key,
                        'action': event_obj.action,
                        'args': args
                    }
                    self._workers.apply_async(run_action, (request, ))


class RecurringLoop(Thread):
    """
    Loop that triggers the recurring action of all the services

    The loop walks over all the services from all the repos. When it find a service with recurring actions,
    it send a command to the main server to ask to execute the action.
    The main server then received the request, create the jobs and execute it asynchronously.
    The main server doesn't wait for the job to complete but instead send the execute of the job to a pool of processes
    that take care of waiting for the job to complete and saving it's state back the db.
    """

    def __init__(self):
        super(RecurringLoop, self).__init__()
        self.logger = j.atyourservice.logger
        self._running = False
        self._workers = Pool()

    def run(self):
        self.logger.info('starting recurring thread')
        self._running = True

        while self.is_alive() and self._running:
            repos = j.atyourservice.reposList()
            for repo in repos:
                self.logger.debug('inspect %s for recurring actions' % repo)
                for service in repo.services:
                    if len(service.model.actionsRecurring) <= 0:
                        continue

                    for action_name, recurring_obj in service.model.actionsRecurring.items():

                        now = j.data.time.epoch
                        if recurring_obj.lastRun == 0 or now > (recurring_obj.lastRun + recurring_obj.period):
                            recurring_obj.lastRun = now
                            service.save()
                            self.logger.info('recurring job for %s' % service)
                            request = {
                                'repo_path': service.aysrepo.path,
                                'service_key': service.model.key,
                                'action': action_name,
                            }
                            try:
                                self._workers.apply_async(run_action, (request, ))
                            except Exception as e:
                                self.logger.error('error: %s' % str(e))

            time.sleep(10)

    def stop(self):
        if self._running:
            self._running = False


if __name__ == '__main__':
    server = Server(host='localhost', port=6379)
    server.start()
