from JumpScale import j
import gevent
import ujson
# from rq import Queue
# import JumpScale.baselib.redisworker
from JumpScale.legacy.redisworker.RedisWorker import RedisWorkerFactory
import crontab
from JumpScale.legacy.jumpscripts.JumpscriptFactory import Jumpscript


class JumpscriptsCmds():

    def __init__(self, daemon=None):
        self.log = j.logger.get('j.legacy.agent.jumpscriptsCmds')
        self.ORDER = 1
        self._name = "jumpscripts"

        if daemon is None:
            return

        self.daemon = daemon
        self.jumpscriptsByPeriod = {}
        self.jumpscripts = {}

        # self.lastMonitorResult=None
        self.lastMonitorTime = None

        self.redis = j.core.db

    def _init(self):
        self.loadJumpscripts(init=True)

    def _adminAuth(self, username, password):
        raise NotImplemented

    def loadJumpscripts(self, path="jumpscripts", session=None, init=False):
        self.log.info("LOAD JUMPSCRIPTS")
        if session is not None:
            self._adminAuth(session.user, session.passwd)

        self.agentcontroller_client = j.clients.agentcontroller.getByInstance()

        self.jumpscriptsByPeriod = {}
        self.jumpscripts = {}

        j.legacy.jumpscripts.loadFromAC(self.agentcontroller_client)

        jspath = j.sal.fs.joinPaths(j.dirs.base, 'apps', 'jsagent', 'jumpscripts')
        if not j.sal.fs.exists(path=jspath):
            raise RuntimeError("could not find jumpscript directory:%s" % jspath)
        self._loadFromPath(jspath)

        self._killGreenLets()

        if not init:
            self._configureScheduling()
            self._startAtBoot()

        j.legacy.processmanager.restartWorkers()

        return "ok"

    def schedule(self):
        self._configureScheduling()
        self._startAtBoot()

    def _loadFromPath(self, path):
        self.startatboot = list()
        jumpscripts = self.agentcontroller_client.listJumpscripts()
        iddict = {(org, name): jsid for jsid, org, name, role in jumpscripts}
        for jscriptpath in j.sal.fs.listFilesInDir(path=path, recursive=True, filter="*.py", followSymlinks=True):
            try:
                js = Jumpscript(path=jscriptpath)
            except Exception as e:
                self.log.error('Failed to load jumpscript [%s]: %s' % (jscriptpath, e))
                continue

            js.id = iddict.get((js.organization, js.name))
            # self.log.info "from local:",
            self._processJumpscript(js, self.startatboot)

    def _processJumpscript(self, jumpscript, startatboot):
        roles = set(j.core.grid.roles)
        if '*' in jumpscript.roles:
            jumpscript.roles.remove('*')
        if jumpscript.enable and roles.issuperset(set(jumpscript.roles)):
            organization = jumpscript.organization
            name = jumpscript.name
            self.jumpscripts["%s_%s" % (organization, name)] = jumpscript

            self.log.info("found jumpscript:%s_%s " % (organization, name))
            # self.jumpscripts["%s_%s" % (organization, name)] = jumpscript
            period = jumpscript.period
            if period is not None:
                if period:
                    if period not in self.jumpscriptsByPeriod:
                        self.jumpscriptsByPeriod[period] = []
                    self.log.info("schedule jumpscript %s on period:%s" % (jumpscript.name, period))
                    self.jumpscriptsByPeriod[period].append(jumpscript)

            if jumpscript.startatboot:
                startatboot.append(jumpscript)

            self.redis.hset("workers:jumpscripts:id", jumpscript.id, ujson.dumps(jumpscript.getDict()))

            if jumpscript.organization != "" and jumpscript.name != "":
                self.redis.hset("workers:jumpscripts:name", "%s__%s" % (jumpscript.organization, jumpscript.name),
                                ujson.dumps(jumpscript.getDict()))

    ####SCHEDULING###

    def _killGreenLets(self, session=None):
        """
        make sure all running greenlets stop
        """
        if session is not None:
            self._adminAuth(session.user, session.passwd)
        todelete = []

        for key, greenlet in j.legacy.processmanager.daemon.greenlets.items():
            if key.find("loop") == 0:
                greenlet.kill()
                todelete.append(key)
        for key in todelete:
            j.core.processmanager.daemon.greenlets.pop(key)

    def _startAtBoot(self):
        for jumpscript in self.startatboot:
            jumpscript.execute()

    def _run(self, period=None, redisw=None):
        if period is None:
            for period in self.jumpscriptsByPeriod.keys():
                self._run(period)

        if period in self.jumpscriptsByPeriod:
            for action in self.jumpscriptsByPeriod[period]:
                action.execute(_redisw=redisw)

    def _loop(self, period):
        redisw = RedisWorkerFactory()
        if isinstance(period, str):
            wait = crontab.CronTab(period).next
        else:
            wait = lambda: period
        while True:
            waittime = wait()
            gevent.sleep(waittime)
            self._run(period, redisw)

    def _configureScheduling(self):
        for period in self.jumpscriptsByPeriod.keys():
            j.legacy.processmanager.daemon.schedule("loop%s" % period, self._loop, period=period)
