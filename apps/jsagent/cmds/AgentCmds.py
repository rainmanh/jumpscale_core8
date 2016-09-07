from JumpScale import j
import gevent
import time
from JumpScale.servers.serverbase import returnCodes


class AgentCmds():
    ORDER = 20

    def __init__(self, daemon=None):
        self._name = "agent"
        self.log = j.logger.get('AgentCmds')
        if daemon == None:
            return
        self.daemon = daemon

        self.redis = j.core.db

    def _init(self):
        self.init()

    def _adminAuth(self, user, password):
        raise NotImplemented

    def init(self, session=None):
        if session is not None:
            self._adminAuth(session.user, session.passwd)

        self._killGreenLets()
        j.legacy.processmanager.daemon.schedule("agent", self.loop)

    def reconnect(self):
        while True:
            try:
                client = j.clients.agentcontroller.getByInstance()
                client.register()
                return client
            except Exception as e:
                self.log.error("Failed to connect to agent controller: %s" % e)
                gevent.sleep(5)

    def loop(self):
        """
        fetch work from agentcontroller & put on redis queue
        """
        client = self.reconnect()
        gevent.sleep(2)
        self.log.info("start loop to fetch work")
        while True:
            try:
                try:
                    self.log.info("check if work")
                    job = client.getWork(transporttimeout=65)
                    if job is not None:
                        self.log.info("WORK FOUND: jobid:%(id)s cmd:%(cmd)s" % job)
                    else:
                        continue
                except Exception as e:
                    self.log.error(e)
                    j.errorconditionhandler.processPythonExceptionObject(e)
                    client = self.reconnect()
                    continue
                job['achost'] = client.ipaddr
                job['nid'] = j.application.whoAmI.nid
                if job["queue"] == "internal":
                    # cmd needs to be executed internally (is for proxy functionality)

                    if job["category"] in self.daemon.cmdsInterfaces:
                        job["resultcode"], returnformat, job["result"] = self.daemon.processRPC(job["cmd"],
                                                                                                data=job["args"],
                                                                                                returnformat="m",
                                                                                                session=None,
                                                                                                category=job[
                                                                                                    "category"])
                        if job["resultcode"] == returnCodes.OK:
                            job["state"] = "OK"
                        else:
                            job["state"] = "ERROR"
                    else:
                        job["resultcode"] = returnCodes.METHOD_NOT_FOUND
                        job["state"] = "ERROR"
                        job["result"] = "Could not find cmd category:%s" % job["category"]
                    client.notifyWorkCompleted(job)
                    continue

                if job["jscriptid"] == None:
                    raise RuntimeError("jscript id needs to be filled in")

                jscriptkey = "%(category)s_%(cmd)s" % job
                if jscriptkey not in j.legacy.processmanager.cmds.jumpscripts.jumpscripts:
                    msg = "could not find jumpscript %s on processmanager" % jscriptkey
                    job['state'] = 'ERROR'
                    job['result'] = msg
                    client.notifyWorkCompleted(job)
                    j.events.bug_critical(msg, "jumpscript.notfound")

                jscript = j.legacy.processmanager.cmds.jumpscripts.jumpscripts[jscriptkey]
                if (jscript.async or job['queue']) and jscript.debug is False:
                    j.legacy.redisworker.execJobAsync(job)
                else:
                    def run(localjob):
                        timeout = gevent.Timeout(localjob['timeout'])
                        timeout.start()
                        try:
                            localjob['timeStart'] = time.time()
                            status, result = jscript.execute(**localjob['args'])
                            localjob['timeStop'] = time.time()
                            localjob['state'] = 'OK' if status else 'ERROR'
                            localjob['result'] = result
                            client.notifyWorkCompleted(localjob)
                        finally:
                            timeout.cancel()

                    gevent.spawn(run, job)
            except Exception as e:
                self.log.error(e)
                # TODO: process python exception
                # j.errorconditionhandler.processPythonExceptionObject(e)

    def _killGreenLets(self, session=None):
        """
        make sure all running greenlets stop
        """
        if session is not None:
            self._adminAuth(session.user, session.passwd)
        todelete = []

        for key, greenlet in j.legacy.processmanager.daemon.greenlets.items():
            if key.find("agent") == 0:
                greenlet.kill()
                todelete.append(key)
        for key in todelete:
            j.legacy.processmanager.daemon.greenlets.pop(key)

    def checkRedisStatus(self, session=None):
        for redisinstance in [j.core.db]:
            running = True
            try:
                running = redisinstance.pint()
            except:
                running = False
            if not running:
                return False
        return True

    def checkRedisSize(self, session=None):
        redisinfo = j.legacy.redisworker.redis.info().split('\r\n')
        info = dict()
        for entry in redisinfo:
            if ':' in entry:
                key, value = entry.split(':')
                info[key] = value
        size = info['used_memory']
        maxsize = 50 * 1024 * 1024
        if j.basetype.float.fromString(size) < maxsize:
            return True
        return False
