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
from JumpScale.clients.redis.RedisQueue import RedisQueue
import socket

processes = list()


class Process():
    def __init__(self):
        self.name = "unknown"
        self.domain = ""
        self.instance = "0"
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
        rss, vms = self.p.get_memory_info()
        return vms != 0

    def _spawnProcess(self):
        if self.logpath == None:
            self.logpath = j.sal.fs.joinPaths(j.dirs.logDir, "processmanager", "logs",
                                                 "%s_%s_%s.log" % (self.domain, self.name, self.instance))
            j.sal.fs.createDir(j.sal.fs.joinPaths(j.dirs.logDir, "processmanager", "logs"))
            stdout = open(self.logpath, 'w')
        else:
            stdout = None

        stdin = subprocess.PIPE
        stdout = sys.stdout
        stderr = sys.stderr
        self.cmds.extend(['-lp', self.logpath])

        try:
            self.p = psutil.Popen(self.cmds, env=self.env, cwd=self.workingdir, stdin=stdin, stdout=stdout,
                                  stderr=stderr, bufsize=0, shell=False)  # f was: subprocess.PIPE
            self.pid = self.p.pid
        except Exception as e:
            print("could not execute:%s\nError:\n%s" % (self, e))

        time.sleep(0.1)
        if self.is_running() == False:
            print("could not execute:%s\n" % (self))
            if j.sal.fs.exists(path=self.logpath):
                log = j.sal.fs.fileGetContents(self.logpath)
                print("log:\n%s" % log)

    def do(self):
        print('A new child %s' % self.name, os.getpid())
        if self.pythonCode != None:
            exec(self.pythonCode)

        os._exit(0)

    def __str__(self):
        return "%s" % self.__dict__

    __repr__ = __str__


class ProcessManager():
    def __init__(self, opts):
        self.opts = opts

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
            while j.sal.nettools.waitConnectionTest(opts.ip, opts.port, 2) == False:
                print("cannot connect to agentcontroller, will retry forever: '%s:%s'" % (opts.ip, opts.port))

            # now register to agentcontroller
            self.acclient = j.clients.legacycontroller.get(opts.ip, port=opts.port, login="root", passwd=opts.password, new=True)
            res = self.acclient.registerNode(hostname=socket.gethostname(),
                                             machineguid=j.application.getUniqueMachineId())

            nid = res["node"]["id"]
            hrd = j.data.hrd.get(j.sal.fs.joinPaths(j.dirs.hrd, 'grid.hrd'))
            hrd.set('id', opts.gid)
            hrd.set('node.id', nid)
            j.application._initWhoAmI(reload=True)

            self.acclient = j.clients.legacycontroller.get(opts.ip, port=opts.port, login="node", new=True)
        else:
            self.acclient = None

    def start(self):

        # self._webserverStart()        
        self._workerStart()

        j.core.grid.init()
        gevent.spawn(self._processManagerStart)

        self.mainloop()

    def _webserverStart(self):
        # start webserver
        server = PMWSServer()
        server.pm = self

        p = Process()
        p.domain = "jumpscale"
        p.name = "web"
        p.instance = "main"
        p.workingdir = "/"
        p.pythonObj = server
        p.pythonCode = "self.pythonObj.start()"
        p.start()
        self.processes.append(p)

    def _processManagerStart(self):
        j.core.processmanager.start()

    def _workerStart(self):
        pwd = '/opt/jumpscale7/apps/jsagent/lib'
        for qname in ["default", "io", "process", "hypervisor"]:
            p = Process()
            p.domain = 'workers'
            p.name = '%s' % qname
            p.instance = 'main'
            p.workingdir = pwd
            p.cmds = ['python', 'worker.py', '-qn', qname, '-i', opts.instance]
            p.restart = True
            p.start()
            self.processes.append(p)

    def mainloop(self):
        i = 0
        while True:
            i += 1
            # print "NEXT:%s\n"%i    
            for p in self.processes[:]:
                # p.refresh()        
                if p.p != None:
                    if not p.is_running():
                        if p.restart:
                            print("%s:%s was stopped restarting" % (p.domain, p.name))
                            p.start()
                        else:
                            print("Process %s has stopped" % p)
                            p.kill()
                            self.processes.remove(p)

            time.sleep(1)
            if len(self.processes) == 0:
                print("no more children")
                # return


@atexit.register
def kill_subprocesses():
    for p in processes:
        p.kill()


parser = cmdutils.ArgumentParser()
parser.add_argument('--grid-id', dest='gid', help='Grid id')
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
processes = pm.processes
pm.services = [item.strip().lower() for item in opts.services.split(",")]

from lib.worker import Worker

# I had to do this in mother process otherwise weird issues caused by gevent !!!!!!!
j.core.osis.client = j.clients.osis.getByInstance()

from gevent.pywsgi import WSGIServer

try:
    pm.start()
except KeyboardInterrupt:
    print("Bye")

j.application.stop()
