#!/usr/bin/env python
from JumpScale import j
import sys
import time
# import psutil
from JumpScale.tools import cmdutils

import multiprocessing

import os

RUNTIME = 24 * 3600


def restart_program():
    """Restarts the current program.
    Note: this function does not return. Any cleanup action (like
    saving data) must be done before calling this function."""
    python = sys.executable
    os.execl(python, python, * sys.argv)


class Worker(object):

    def __init__(self, queuename):
        self.actions = {}
        self.clients = dict()
        self.acclient = None
        self.queuename = queuename
        self.starttime = time.time()

    def processAction(self, action):
        self.job_controller.delete("workers:action:%s" % self.queuename)
        if action == "RESTART":
            self.log("RESTART ASKED")
            j.application.stop(0, True)
            restart_program()

        if action == "RELOAD":
            self.log("RELOAD ASKED")
            self.actions = {}

    def execute(self, *args, **kwargs):
        if self.debug:
            result = self.module.action(*args, **kwargs)
            return True, result
        else:
            def helper(pipe):
                try:
                    result = self.executeInProcess(*args, **kwargs)
                    pipe.send(result)
                except Exception as e:
                    try:
                        result = self._getECO(e)
                    except Exception as e:
                        msg = 'Failed parsing original exception: %s' % e
                        result = j.exception.RuntimeError(msg=msg)
                    pipe.send((False, result))

            ppipe, cpipe = multiprocessing.Pipe()
            proc = multiprocessing.Process(target=helper, args=(cpipe,))
            proc.start()
            cpipe.close()
            proc.join(self.timeout)
            if proc.is_alive():
                proc.terminate()
                return False, "TIMEOUT"
            try:
                return ppipe.recv()
            except:
                msg = 'Job died unexpectedly'
                result = j.exception.RuntimeError(msg=msg)
                return False, result

    def run(self):
        self.log("STARTED")
        while True:
            if self.starttime + RUNTIME < time.time():
                self.log("Running for %s seconds restarting" % RUNTIME)
                restart_program()
            try:
                self.log("check if work")
                job = self.job_controller.queue_pop(self.queuename, timeout=10)
                jtype = None  # figure out how to set/get jtype. For now, None is wonderful
            except Exception as e:
                if str(e).find("Could not find queue to execute job") != -1:
                    # create queue
                    self.log("could not find queue")
                else:
                    j.exceptions.RuntimeError("Could not get work from redis, is redis running?", "workers.getwork", e)
                time.sleep(10)
                continue
            if jtype == "action":
                self.processAction(job)
                continue
            if job:
                try:
                    import ipdb
                    ipdb.set_trace()
                    job.timeStart = time.time()
                    status, result = self.execute(**job.args)
                    self.job_controller.delete("workers:inqueuetest", job.guid())
                    j.logger.enabled = True
                    if status:
                        job.result = result
                        job.state = "OK"
                        job.resultcode = 0
                    else:
                        if isinstance(result, str):
                            job.state = result
                        else:
                            eco = result
                            eco.jid = job.guid
                            eco.category = "workers.executejob"

                            if job.id < 1000000:
                                eco.process()
                            else:
                                self.log(eco)
                            # j.events.bug_warning(msg,category="worker.jscript.notexecute")
                            # self.loghandler.logECO(eco)
                            job.state = "ERROR"
                            eco.tb = None
                            job.result = eco.__dict__
                            job.resultcode = 1

                    # ok or not ok, need to remove from queue test
                    # thisin queue test is done to now execute script multiple time
                    # self.notifyWorkCompleted(job)
                finally:
                    j.application.jid = 0

    def notifyWorkCompleted(self, job):
        job.timeStop = int(time.time())

        if job.internal:
            # means is internal job
            self.job_controller.set("workers:jobs:%s" % job.id, j.data.serializer.json.dumps(job.__dict__), ex=60)
            self.job_controller.rpush("workers:return:%s" % job.id, time.time())
            self.job_controller.expire("workers:return:%s" % job.id, 60)
        try:
            acclient = self.getClient(job)
        except Exception as e:
            j.exceptions.RuntimeError("could not report job in error to agentcontroller",
                                      category='workers.errorreporting', e=e)
            return

        def reportJob():
            try:
                acclient.notifyWorkCompleted(job.__dict__)
            except Exception as e:
                j.exceptions.RuntimeError("could not report job in error to agentcontroller",
                                          category='workers.errorreporting', e=e)
                return

        # jumpscripts coming from AC
        if job.state != "OK":
            self.job_controller.expire("workers:jobs:%s" % job.id, 60)
            reportJob()
        else:
            if job.log or job.wait:
                reportJob()
            # we don't have to keep status of local job result, has been forwarded to AC
            if not job.internal:
                self.job_controller.delete("workers:jobs:%s" % job.id)

    def log(self, message, category='', level=5, time=None):
        if time is None:
            time = j.data.time.getLocalTimeHR()
        msg = "%s:worker:%s:%s" % (time, self.queuename, message)
        try:
            print(msg)
        except IOError:
            pass
        if self.logFile != None:
            msg = msg + "\n"
            self.logFile.write(msg)

if __name__ == '__main__':
    parser = cmdutils.ArgumentParser()
    parser.add_argument("-q", '--queuename', help='Queue name', required=True)
    # parser.add_argument("-i", '--instance', help='JSAgent instance', required=True)
    # parser.add_argument("-lp", '--logpath', help='Logging file path', required=False, default=None)

    opts = parser.parse_args()

    j.application.start("jumpscale:worker:%s" % opts.queuename)

    j.logger.consoleloglevel = 2
    j.logger.maxlevel = 7

    worker = Worker(opts.queuename)
    worker.run()
