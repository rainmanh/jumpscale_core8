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
import socket
from JumpScale.tools import cmdutils

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
        self.pm = j.tools.cuisine.local.processmanager.get('tmux')

    def start(self):
        if self.cmds != []:
            self._spawnProcess()
        if self.pythonCode is not None:
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
        if self.p is not None:
            try:
                self.p.kill()
            except Exception as e:
                print(e)

    def is_running(self):
        try:
            rss, vms = self.p.memory_info()[:2]
        except Exception:  # TODO
            return False
        return vms != 0

    def _spawnProcess(self):
        if self.logpath is None:
            self.logpath = j.sal.fs.joinPaths(j.dirs.logDir, "processmanager", "logs", "%s_%s_%s.log" % (self.domain, self.name, self.instance))
            j.sal.fs.createDir(j.sal.fs.joinPaths(j.dirs.logDir, "processmanager", "logs"))
            stdout = open(self.logpath, 'w')
        else:
            stdout = None

        stdin = subprocess.PIPE
        stdout = sys.stdout
        stderr = sys.stderr
        self.cmds.extend(['-lp', self.logpath])

        try:
            cmd = ' '.join(self.cmds)
            self.pm.ensure('worker_%i' % j.data.idgenerator.generateRandomInt(0, 100), cmd, path=self.workingdir)
            # self.p = psutil.Popen(self.cmds, env=self.env, cwd=self.workingdir, stdin=stdin, stdout=stdout, stderr=stderr, bufsize=0, shell=False)  # f was: subprocess.PIPE
            # self.pid = self.p.pid
        except Exception as e:
            print(("could not execute:%s\nError:\n%s" % (self, e)))

        time.sleep(0.1)
        if self.is_running() == False:
            print(("could not execute:%s\n" % (self)))
            if j.sal.fs.exists(path=self.logpath):
                log = j.sal.fs.fileGetContents(self.logpath)
                print(("log:\n%s" % log))

    def do(self):
        print(('A new child %s' % self.name, os.getpid()))
        if self.pythonCode is not None:
            exec(self.pythonCode)

        os._exit(0)

    def __str__(self):
        return "%s" % self.__dict__

    __repr__ = __str__


class ProcessManager():
    def __init__(self, reset=False):

        self.processes = list()
        self.services = list()

        self.dir_data = j.sal.fs.joinPaths(j.dirs.base, "jsagent_data")
        self.dir_actions = j.sal.fs.joinPaths(self.dir_data, "actions")
        j.sal.fs.createDir(self.dir_data)

        self.aysdb = j.atyourservice.db.getDB('agent')

        self.redis_queues = {}
        # self.redis_queues["io"] = self.aysdb.getQueue("workers:work:io")
        # self.redis_queues["hypervisor"] = self.aysdb.getQueue("workers:work:hypervisor")
        self.redis_queues["default"] = self.aysdb.getQueue("workers:work:default")
        # self.redis_queues["process"] = self.aysdb.getQueue("workers:work:process")

        self.pm = j.tools.cuisine.local.processmanager.get('tmux')

        self.hrd = {}

    def start(self):

        # self._webserverStart()
        self._workerStart()

        self.mainloop()

    def _workerStart(self):
        pwd = '/opt/code/github/jumpscale/jumpscale_core8/lib/JumpScale/baselib/atyourservice/AYSManager'
        for qname in ["default"]:  # , "io", "process", "hypervisor"]:
            p = Process()
            p.domain = 'workers'
            p.name = '%s' % qname
            p.instance = 'main'
            p.workingdir = pwd
            p.cmds = ['python', 'worker.py', '-q', qname, '-i', opts.instance]
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
                if p.p is not None:
                    if not p.is_running():
                        if p.restart:
                            print(("%s:%s was stopped restarting" % (p.domain, p.name)))
                            p.start()
                        else:
                            print(("Process %s has stopped" % p))
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
parser.add_argument("-i", '--instance', default="0", help='jsagent instance', required=False)
parser.add_argument("-r", '--reset', action='store_true', help='jsagent reset', required=False, default=False)
parser.add_argument("-s", '--services', help='list of services to run e.g heka, agentcontroller,web', required=False, default="")

opts = parser.parse_args()

from worker import Worker

# I had to do this in mother process otherwise weird issues caused by gevent !!!!!!!

pm = ProcessManager()
from gevent.pywsgi import WSGIServer

try:
    pm.start()
except KeyboardInterrupt:
    print("Bye")

j.application.stop()
