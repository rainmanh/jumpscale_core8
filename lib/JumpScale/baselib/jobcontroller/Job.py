from JumpScale import j
from JumpScale.core.errorhandling.ErrorConditionObject import ErrorConditionObject
import importlib
import colored_traceback
import pygments.lexers
import cProfile
from contextlib import contextmanager
from io import StringIO
import sys
import asyncio
import functools

colored_traceback.add_hook(always=True)

def _execute_cb(job, epoch, future):
    """
    callback call after a job has finished executing
    job: is the job object
    epoch: is the epoch when the job started
    future: future that hold the result of the job execution
    """
    service_action_obj = None
    if job.service is not None:
        # if the action is a reccuring action, save last execution time in model
        action_name = job.model.dbobj.actionName
        if action_name in job.service.model.actionsRecurring:
            job.service.model.actionsRecurring[action_name].lastRun = epoch
            service_action_obj = job.service.model.actions[action_name]

    exception = future.exception()
    if exception is not None:
        job.state = 'error'
        job.model.dbobj.state = 'error'
        if service_action_obj:
            service_action_obj.state = 'error'
        eco = j.errorconditionhandler.processPythonExceptionObject(exception)
        job._processError(eco)
    else:
        job.state = 'ok'
        job.model.dbobj.state = 'ok'
        if service_action_obj:
            service_action_obj.state = 'ok'

        log_enable = True
        if service_action_obj:
            log_enable = j.core.jobcontroller.db.actions.get(service_action_obj.actionKey).dbobj.log
        if log_enable:
            _, stdout, stderr = future.result()
            if stdout != '':
                job.model.log(msg=stdout, level=5, category='out')
            if stderr != '':
                job.model.log(msg=stderr, level=5, category='err')
        job.logger.info("job {} done sucessfuly".format(str(job)))
    job.save()

@contextmanager
def stdstreams_redirector(stdout, stderr):
    """
    redirect std and stderr to buffer
    """
    yield
    # old_stdout = sys.stdout
    # sys.stdout = stdout
    # old_stderr = sys.stderr
    # sys.stderr = stderr
    # try:
    #     yield
    # finally:
    #     sys.stdout = old_stdout
    #     sys.stderr = old_stderr

def wraper(args):
    stdout = StringIO()
    stderr = StringIO()
    func = args[0]
    with stdstreams_redirector(stdout, stderr):
        if len(args) >= 2:
            result = func(*args[1:])
        else:
            result = func()
    return (result, stdout.getvalue(), stderr.getvalue())


class Job():
    """
    is what needs to be done for 1 specific action for a service
    """

    def __init__(self, model):
        self.logger = j.atyourservice.logger
        self.model = model
        self._action = None
        self._service = None
        self._source = None
        self.saveService = True

    @property
    def action(self):
        if self._action is None:
            self._action = j.core.jobcontroller.db.actions.get(self.model.dbobj.actionKey)
        return self._action

    @property
    def sourceToExecute(self):
        if self._source is None:
            s = """
            $imports
            from JumpScale import j

            def action($args):
            $source
            """
            s = j.data.text.strip(s)
            s = s.replace("$imports", '\n'.join(self.action.imports))
            code = self.action.dbobj.code
            code = j.data.text.indent(code, 4)

            s = s.replace("$source", code)
            s = s.replace("$args", self.action.argsText)
            self._source = s
        return self._source

    @property
    def sourceToExecutePath(self):
        path = j.sal.fs.joinPaths(j.dirs.TMPDIR, "actions", self.action.dbobj.actorName, self.action.dbobj.name + ".py")
        j.sal.fs.createDir(j.sal.fs.joinPaths(j.dirs.TMPDIR, "actions", self.action.dbobj.actorName))
        j.sal.fs.writeFile(path, self.sourceToExecute)
        return path

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
    def method(self):
        if self.action.key not in j.core.jobcontroller._methods:
            loader = importlib.machinery.SourceFileLoader(self.action.key, self.sourceToExecutePath)
            handle = loader.load_module(self.action.key)
            method = eval("handle.action")
            j.core.jobcontroller._methods[self.action.key] = method
        return j.core.jobcontroller._methods[self.action.key]

    @property
    def service(self):
        if self._service is None:
            if self.model.dbobj.actorName != "":
                repo = j.atyourservice.aysRepos.get(path=self.model.dbobj.repoKey)
                serviceModel = repo.db.services.get(self.model.dbobj.serviceKey)
                self._service = serviceModel.objectGet(repo)
        return self._service

    def _processError(self, eco):
        logObj = self.model._logObjNew()

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
            if self.saveService:
                self.service.reload()
                if self.model.dbobj.actionName in self.service.model.actions:
                    service_action_obj = self.service.model.actions[self.model.dbobj.actionName]
                    service_action_obj.state = str(self.model.dbobj.state)
                self.service.saveAll()

    def executeInProcess(self):
        """
        execute the job in the process, capture output when possible
        if debug job then will not capture output so our debugging features work
        """
        return self.execute()
        # # to make sure we don't put it in the profiler
        # self.method
        #
        # if self.service.aysrepo.model.no_exec is False:
        #
        #     if self.model.dbobj.profile:
        #         pr = cProfile.Profile()
        #         pr.enable()
        #
        #     try:
        #         if self.model.dbobj.actorName != "":
        #             res = self.method(job=self)
        #         else:
        #             res = self.method(**self.model.args)
        #
        #     except Exception as e:
        #         self.model.dbobj.state = 'error'
        #         eco = j.errorconditionhandler.processPythonExceptionObject(e)
        #         self._processError(eco)
        #         log = self.model.dbobj.logs[-1]
        #         print(self.str_error(log.log))
        #         raise j.exceptions.RuntimeError("could not execute job:%s" % self)
        #
        #     finally:
        #         if self.model.dbobj.profile:
        #             pr.create_stats()
        #             # TODO: *1 this is slow, needs to be fetched differently
        #             stat_file = j.sal.fs.getTempFileName()
        #             pr.dump_stats(stat_file)
        #             self.model.dbobj.profileData = j.sal.fs.fileGetBinaryContents(stat_file)
        #             j.sal.fs.remove(stat_file)
        # else:
        #     res = None
        #
        # self.model.dbobj.state = 'ok'
        #
        # self.model.result = res
        # self.save()
        # return res

    def execute(self):
        """
        this method returns a future
        you need to await it to schedule it the event loop.
        the future return a tuple containing (result, stdout, stderr)

        ex: result, stdout, stderr = await job.execute()
        """
        loop = asyncio.get_event_loop()
        # for now use default ThreadPoolExecutor
        future = loop.run_in_executor(None, wraper, (self.method, self))
        now = j.data.time.epoch
        future.add_done_callback(functools.partial(_execute_cb, self, now))

        self.model.dbobj.state = 'running'
        self.save()
        return future

        # if self.service.aysrepo.model.no_exec is True:
        #     return None

        # # TODO improve debug detection
        # if self.model.dbobj.debug is False:
        #     debugInCode = self.sourceToExecute.find('ipdb') != -1 or self.sourceToExecute.find('IPython') != -1
        #     self.model.dbobj.debug = debugInCode
        #
        # # can be execute in paralle so we don't wait for end of execution here.
        # if self.model.dbobj.debug:
        #     process = self.executeInProcess()
        # else:
        #     process = j.core.processmanager.startProcess(self.method, {'job': self})
        #
        # return process

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
