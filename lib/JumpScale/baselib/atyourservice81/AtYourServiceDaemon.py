from JumpScale import j
import signal
import time
from multiprocessing import Process, Pool


class Server:
    """AtYourService server"""

    def __init__(self, host="localhost", port=6379, unixsocket=None):
        self.host = host
        self.port = port
        self.unixsocket = unixsocket
        self._server = j.servers.kvs.getRedisStore("ays_server", namespace='db', host=self.host, port=self.port, unixsocket=self.unixsocket)
        self.logger = j.atyourservice.logger

        self._recurring_loop = RecurringLoop(j.clients.atyourservice.get(host=self.host, port=self.port, unixsocket=self.unixsocket))
        self._waiting_jobs = Pool(processes=32)

        # self._set_signale_handler()

        self._running = False

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
            payload = self._server.queueGet('command', timeout=2)
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
            self.logger.info("stopping recurring thread")
            self._recurring_loop.stop()
            # FIXME: why:  assert self._parent_pid == os.getpid(), 'can only join a child process'
            # self._recurring_loop.join()

        if self._running:
            self._running = False
            self.logger.info("stopping server")

        self.logger.info("wait for all jobs to finish")
        self._waiting_jobs.close()
        self._waiting_jobs.join()

    def _dispatch(self, request):
        self.logger.info('dispatch request %s' % request)

        # TODO: implemet other commands
        if request['command'] == 'execute':
            self._execute(request)

    def _execute(self, request):
        self._waiting_jobs.apply_async(process_job, (request,))


def process_job(request):
    """
    this task creates a job from the request information, wait for the job to complete and save the state of the job back to the database
    """
    logger = j.atyourservice.logger
    try:
        repo = j.atyourservice.repoGet(request['repo_path'])
        service_model = repo.db.service.get(request['service_key'])
        service = service_model.objectGet(repo)
    except Exception as e:
        logger.error("Can't execute action: %s" % str(e))
        return

    logger.info('execute %s on %s' % (request['action_name'], service))
    action = request['action_name']
    job = service.getJob(request['action_name'])

    now = j.data.time.epoch
    p = job.execute()

    while not p.isDone():
        p.wait()

    # if the action is a reccuring action, save last execution time in model
    if action in service.model.actionsRecurring:
        service.model.actionsRecurring[action].lastRun = now

    service_action_obj = service.model.actions[action]

    if p.state != 'success':
        job.model.dbobj.state = 'error'
        service_action_obj.state = 'error'
        # processError creates the logs entry in job object
        job._processError(p.error)
    else:
        job.model.dbobj.state = 'ok'
        service_action_obj.state = 'ok'

        log_enable = j.core.jobcontroller.db.action.get(service_action_obj.actionKey).dbobj.log
        if log_enable:
            job.model.log(msg=p.stdout, level=5, category='out')
            job.model.log(msg=p.stderr, level=5, category='err')

    job.model.save()
    service.save()
    j.atyourservice.logger.info('job %s for %s finished' % (action, service.model.key))
    return 'done'


class RecurringLoop(Process):
    """
    Loop that triggers the recurring action of all the services

    The loop walks over all the services from all the repos. When it find a service with recurring actions,
    it send a command to the main server to ask to execute the action.
    The main server then received the request, create the jobs and execute it asynchronously.
    The main server doesn't wait for the job to complete but instead send the execute of the job to a pool of processes
    that take care of waiting for the job to complete and saving it's state back the db.
    """

    def __init__(self, client):
        super(RecurringLoop, self).__init__()
        self._client = client
        self.logger = j.atyourservice.logger
        self._running = False

    def run(self):
        self.logger.info('starting recurring thread')
        self._running = True

        while self.is_alive() and self._running:
            # TODO loop over all repos
            repo = j.atyourservice.get()
            for service in repo.services:
                if len(service.model.actionsRecurring) <= 0:
                    continue

                for action_name, recurring_obj in service.model.actionsRecurring.items():

                    now = j.data.time.epoch
                    if recurring_obj.lastRun == 0 or now > (recurring_obj.lastRun + recurring_obj.period):
                        self._client.do('execute', args={
                            'repo_path': repo.path,
                            'service_key': service.model.key,
                            'action_name': action_name
                        })
                        recurring_obj.lastRun = now

            time.sleep(1)

    def stop(self):
        if self._running:
            self._running = False


if __name__ == '__main__':
    server = Server(host='localhost', port=6379)
    server.start()
