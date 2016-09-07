# gevent monkey patching should be done as soon as possible dont move!
import gevent
import gevent.monkey

gevent.monkey.patch_all()

from JumpScale import j

j.application.start("jsagent")
import time
import sys
import atexit
import psutil
import os
import subprocess
from JumpScale.tools import cmdutils
from JumpScale.core.redis import RedisQueue
import socket

processes = list()


class Process():
    def __init__(self):
        self.log = j.logger.get('Process')
        self.name = "unknown"
        self.domain = ""
        self.pid = 0
        self.workingdir = None
        self.cmds = []
        self.env = None
        self.pythonArgs = {}
        self.pythonObj = None
        self.pythonCode = None
        self.logpath = None
        self.ports = []
        self.psstring = ""
        self.sync = False
        self.restart = False
        self.p = None

    def start(self):
        if self.cmds != []:
            self._spawnProcess()
        if self.pythonCode != None:
            if self.sync:
                self.do()
            else:
                self.pid = os.fork()
                if self.pid == 0:
                    self.do()
                else:
                    self.refresh()

    def refresh(self):
        self.p = psutil.Process(self.pid)

    def kill(self):
        if self.p != None:
            self.p.kill()

    def is_running(self):
        mem = self.p.memory_info()
        return mem.vms != 0

    def _spawnProcess(self):
        if self.logpath is None:
            self.logpath = j.sal.fs.joinPaths(j.dirs.logDir, "processmanager", "logs",
                                                 "%s_%s.log" % (self.domain, self.name))
            j.sal.fs.createDir(j.sal.fs.joinPaths(j.dirs.logDir, "processmanager", "logs"))
            stdout = open(self.logpath, 'w')
        else:
            stdout = None

        stdin = subprocess.PIPE
        stdout = sys.stdout
        stderr = sys.stderr
        self.cmds.extend(['-l', self.logpath])

        try:
            self.p = psutil.Popen(self.cmds, env=self.env, cwd=self.workingdir, stdin=stdin, stdout=stdout,
                                  stderr=stderr, bufsize=0, shell=False)  # f was: subprocess.PIPE
            self.pid = self.p.pid
        except Exception as e:
            self.log.error("could not execute:%s\nError:\n%s" % (self, e))

        time.sleep(0.1)
        if self.is_running() is False:
            self.log.warning("could not execute:%s\n" % (self))
            if j.sal.fs.exists(path=self.logpath):
                log = j.sal.fs.fileGetContents(self.logpath)
                self.log.error(log)

    def do(self):
        self.log.info('A new child %s' % self.name, os.getpid())
        if self.pythonCode != None:
            exec(self.pythonCode)

        os._exit(0)

    def __str__(self):
        return "%s" % self.__dict__

    __repr__ = __str__


class ProcessManager():
    def __init__(self, opts):
        self.opts = opts
        self.log = j.logger.get('ProcessManager')

        self.processes = list()
        self.services = list()

        self.dir_data = j.sal.fs.joinPaths(j.dirs.base, "jsagent_data")
        self.dir_hekadconfig = j.sal.fs.joinPaths(self.dir_data, "dir_hekadconfig")
        self.dir_actions = j.sal.fs.joinPaths(self.dir_data, "actions")
        j.sal.fs.createDir(self.dir_data)
        self.redis_mem = j.core.db

        self.redis_queues = {}
        self.redis_queues["io"] = RedisQueue(self.redis_mem, "workers:work:io")
        self.redis_queues["hypervisor"] = RedisQueue(self.redis_mem, "workers:work:hypervisor")
        self.redis_queues["default"] = RedisQueue(self.redis_mem, "workers:work:default")
        self.redis_queues["process"] = RedisQueue(self.redis_mem, "workers:work:process")

        j.processmanager = self

        # self.hrd = j.application.instanceconfig
        if opts.ip != "":
            # processmanager enabled
            while j.sal.nettools.waitConnectionTest(opts.ip, opts.port, 2) is False:
                self.log.info("cannot connect to agentcontroller, will retry forever: '%s:%s'" % (opts.ip, opts.port))

            # now register to agentcontroller
            self.acclient = j.legacy.agentcontroller.get(opts.ip, port=opts.port, login='root', passwd=opts.password, new=True)
            res = self.acclient.registerNode(hostname=socket.gethostname(),
                                             machineguid=j.application.getUniqueMachineId())

            nid = res["node"]["id"]
            hrd = j.data.hrd.get(j.sal.fs.joinPaths(j.dirs.hrd, 'grid.hrd'))
            hrd.set('id', opts.gid)
            hrd.set('node.id', nid)
            j.application._initWhoAmI(reload=True)

            self.acclient = j.legacy.agentcontroller.get(opts.ip, port=opts.port, login="node", new=True)
        else:
            self.acclient = None

        self._monkey_patch()

    def _getClient(self, *args, **kwargs):
        return j.legacy.agentcontroller.get(opts.ip, port=opts.port, login="node", passwd=opts.password, new=True)

    def _monkey_patch(self):
        j.clients.agentcontroller.getByInstance = self._getClient

    def start(self):
        self._workerStart()

        j.core.grid.init()
        gevent.spawn(self._processManagerStart)

        self.mainloop()

    def _processManagerStart(self):
        j.legacy.processmanager.start(self.acclient)

    def _workerStart(self):
        pwd = j.sal.fs.joinPaths(os.path.abspath(''), 'lib')
        for qname in ["default", "io", "process", "hypervisor"]:
            p = Process()
            p.domain = 'workers'
            p.name = '%s' % qname
            p.workingdir = pwd
            p.env = os.environ
            p.cmds = ['python3.5', 'worker.py', '-q', qname, '--controller-ip', self.opts.ip, '--controller-port', str(self.opts.port)]
            p.restart = True
            p.start()
            self.processes.append(p)

    def mainloop(self):
        i = 0
        while True:
            i += 1
            # self.log.info "NEXT:%s\n"%i    
            for p in self.processes[:]:
                # p.refresh()        
                if p.p != None:
                    if not p.is_running():
                        if p.restart:
                            self.log.info("%s:%s was stopped restarting" % (p.domain, p.name))
                            p.start()
                        else:
                            self.log.info("Process %s has stopped" % p)
                            p.kill()
                            self.processes.remove(p)

            time.sleep(1)
            if len(self.processes) == 0:
                self.log.info("no more children")
                # return

parser = cmdutils.ArgumentParser()
parser.add_argument('--grid-id', dest='gid', type=int, default='1', help='Grid id')
parser.add_argument('--services', help='list of services to run e.g heka, agentcontroller,web', required=False,
                    default="")

parser.add_argument('--controller-ip', dest='ip', default='localhost', help='Agent controller address')
parser.add_argument('--controller-port', dest='port', type=int, default=4444, help='Agent controller port')
parser.add_argument('--controller-login', dest='login', default='node', help='Agent controller login')
parser.add_argument('--controller-password', dest='password', default='', help='Agent controller password')

opts = parser.parse_args()

# j.application.instanceconfig = j.application.getAppInstanceHRD('jsagent', 'main')

# first start processmanager with all required stuff
pm = ProcessManager(opts)
@atexit.register
def kill_subprocesses():
    for p in pm.processes:
        p.kill()

pm.services = [item.strip().lower() for item in opts.services.split(",")]

try:
    pm.start()
except KeyboardInterrupt:
    j.logger.log("Bye")

j.application.stop()
