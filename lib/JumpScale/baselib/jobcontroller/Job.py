from JumpScale import j
from JumpScale.baselib.jobcontroller.SourceLoader import SourceLoader
from JumpScale.core.errorhandling.ErrorConditionObject import ErrorConditionObject
import importlib
import types
import colored_traceback
import pygments.lexers
import cProfile
from contextlib import contextmanager
import sys
import asyncio
import functools
import logging
import traceback

colored_traceback.add_hook(always=True)

def _execute_cb(job, future):
    """
    callback call after a job has finished executing
    job: is the job object
    future: future that hold the result of the job execution
    """
    if job._cancelled is True:
        return

    service_action_obj = None

    if job.service is not None:
        action_name = job.model.dbobj.actionName
        if action_name in job.service.model.actions:
            service_action_obj = job.service.model.actions[action_name]
        if action_name in job.service.model.actionsRecurring and service_action_obj:
            # if the action is a reccuring action, save last execution time in model
            service_action_obj.lastRun = j.data.time.epoch
    exception = None
    futurecancelled = False
    try:
        exception = future.exception()
    except:  # CancelledError
        futurecancelled = True
        job.logger.info("****Future was cancelled")
        job.state = 'error'
        job.model.dbobj.state = 'error'
        job.save()

    if exception is not None or futurecancelled:
        job.state = 'error'
        job.model.dbobj.state = 'error'
        if service_action_obj:
            service_action_obj.state = 'error'
        if job.service:
            job.service.model.dbobj.state = 'error'

        ex = exception if exception is not None else TimeoutError()
        eco = j.errorconditionhandler.processPythonExceptionObject(ex)
        job._processError(eco)

        if exception:
            tb_lines = [line.rstrip('\n') for line in traceback.format_exception(exception.__class__, exception, exception.__traceback__)]
            job.logger.error('\n'.join(tb_lines))
    else:
        job.state = 'ok'
        job.model.dbobj.state = 'ok'
        if service_action_obj:
            service_action_obj.state = 'ok'
        if job.service:
            job.service.model.dbobj.state = 'ok'

        job.logger.info("job {} done sucessfuly".format(str(job)))

    job.save()

@contextmanager
def generate_profile(job):
    """
    context manager that generate profile of the code it wrap
    """
    if job.model.dbobj.profile is False:
        yield
    else:
        try:
            pr = cProfile.Profile()
            pr.enable()
            yield
        finally:
            pr.create_stats()
            # TODO: *1 this is slow, needs to be fetched differently
            stat_file = j.sal.fs.getTempFileName()
            pr.dump_stats(stat_file)
            job.model.dbobj.profileData = j.sal.fs.fileGetBinaryContents(stat_file)
            j.sal.fs.remove(stat_file)

class JobHandler(logging.Handler):
    def __init__(self, job_model, level=logging.NOTSET):
        super().__init__(level=level)
        self._job_model = job_model

    def emit(self, record):
        if record.levelno <= 20:
            category = 'msg'
        elif 20 < record.levelno <= 30:
            category = 'alert'
        else:
            category = 'errormsg'
        self._job_model.log(msg=record.getMessage(), level=record.levelno, category=category, epoch=int(record.created), tags='')

class Job():
    """
    is what needs to be done for 1 specific action for a service
    """

    def __init__(self, model):
        self.model = model
        self._cancelled = False
        self._action = None
        self._service = None
        self._future = None
        self.saveService = True
        self._sourceLoader = None
        self.logger = j.logger.get('j.jobcontroller.job.{}'.format(self.model.key))
        self._logHandler = JobHandler(self.model)
        self.logger.addHandler(self._logHandler)

    def __del__(self):
        self.cleanup()

    def cleanup(self):
        """
        clean the logger handler from the job object so it doesn't make the job stays in memory
        """
        self.logger.removeHandler(self._logHandler)
        self._logHandler = None
        self.logger = None

    @property
    def action(self):
        if self._action is None:
            self._action = j.core.jobcontroller.db.actions.get(self.model.dbobj.actionKey)
        return self._action

    def printLogs(self):
        logs = list()
        for log in self.model.dbobj.logs:
            logs.append(("{epoch} - {category}: {log}".format(
                epoch=j.data.time.epoch2HRDateTime(log.epoch),
                category=log.category,
                log=log.log
            )))
        logs = '\n'.join(logs)
        print(logs)
        return logs

    @property
    def sourceLoader(self):
        if self._sourceLoader is None:
            if self._service is None:
                raise j.exceptions.RuntimeError("can't dynamicly load action code, no service present in job object")
            self._sourceLoader = SourceLoader(self._service)
        return self._sourceLoader

    @property
    def method(self):
        return self.sourceLoader.get_method(self.model.dbobj.actionName)

    @property
    def service(self):
        if self._service is None:
            if self.model.dbobj.actorName != "":
                repo = j.atyourservice.aysRepos.get(path=self.model.dbobj.repoKey)
                try:
                    self._service = repo.serviceGetByKey(self.model.dbobj.serviceKey)
                except j.exceptions.NotFound:
                    self.logger.warning("job {} tried to access a non existing service {}".format(self,self.model.dbobj.serviceKey ))
                    return None
        return self._service

    @service.setter
    def service(self, value):
        self._service = value
        self.model.dbobj.serviceKey = value.model.key

    def _processError(self, eco):

        if j.data.types.string.check(eco):
            # case it comes from the result of the processmanager
            eco = j.data.serializer.json.loads(eco)

            epoch = eco['epoch']
            if eco['_traceback'] != '':
                category = 'trace'
                msg = eco['_traceback']
            elif eco['errormessage'] != '':
                category = 'errormsg'
                msg = eco['errormessage']
            else:
                raise j.exceptions.RuntimeError("error message empty, can't process error")

            level = int(eco['level'])
            tags = eco['tags']

        elif isinstance(eco, ErrorConditionObject):
            epoch = eco.epoch
            if eco._traceback != '':
                category = 'trace'
                msg = eco._traceback
            elif eco.errormessage != '':
                category = 'errormsg'
                msg = eco.errormessage
            else:
                raise j.exceptions.RuntimeError("error message empty, can't process error")

            level = eco.level
            tags = eco.tags

        self.model.log(
            msg=msg,
            level=level,
            category=category,
            epoch=epoch,
            tags=tags)

        self.save()

    def error(self, errormsg, level=1, tags=""):
        self.model.log(
            msg=errormsg,
            level=level,
            category="errormsg",
            tags=tags)
        self.save()
        raise RuntimeError(errormsg)

    def save(self):
        self.model.save()
        if self.saveService and self.service is not None:
            if self.model.dbobj.actionName in self.service.model.actions:
                service_action_obj = self.service.model.actions[self.model.dbobj.actionName]
                service_action_obj.state = str(self.model.dbobj.state)
            self.service.saveAll()

    def executeInProcess(self):
        """
        deprecated, all jobs are exected in process now.
        it's now a synonyme of execute()
        """
        return self.execute()

    def execute(self):
        """
        this method returns a future
        you need to await it to schedule it the event loop.
        the future return a tuple containing (result, stdout, stderr)

        ex: result, stdout, stderr = await job.execute()
        """
        # for now use default ThreadPoolExecutor
        if self.model.dbobj.debug is False:
            self.model.dbobj.debug = self.sourceLoader.source.find('ipdb') != -1 or \
                                     self.sourceLoader.source.find('IPython') != -1

        loop = asyncio.get_event_loop()
        self._future = loop.run_in_executor(None, self.method, self)
        # register callback to deal with logs and state of the job after execution
        self._future.add_done_callback(functools.partial(_execute_cb, self))

        if self.service is not None and self.model.dbobj.actionName in self.service.model.actions:
            service_action_obj = self.service.model.actions[self.model.dbobj.actionName]
            service_action_obj.state = 'running'

        self.model.dbobj.state = 'running'

        self.save()
        return self._future

    async def cancel(self):
        self._cancelled = True
        if self._future:
            self._future.remove_done_callback(_execute_cb)
            self._future.cancel()
            try:
                await self._future
            except asyncio.CancelledError:
                self.logger.info("job {} cancelled".format(self))


    def str_error(self, error):
        out = 'Error of %s:' % str(self)
        formatter = pygments.formatters.Terminal256Formatter(style=pygments.styles.get_style_by_name("vim"))

        if error.__str__() != "":
            out += "\n*TRACEBACK*********************************************************************************\n"

            lexer = pygments.lexers.get_lexer_by_name("pytb", stripall=True)
            tb_colored = pygments.highlight(error.__str__(), lexer, formatter)
            out += tb_colored

        out += "\n\n******************************************************************************************\n"
        return out

    def __repr__(self):
        out = "job: %s!%s (%s)" % (
            (self.model.dbobj.actorName, self.model.dbobj.serviceName, self.model.dbobj.actionName))
        return out

    __str__ = __repr__
