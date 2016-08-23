from JumpScale import j

import sys
import psutil
import importlib
import time


class Dummy:
    pass


class DummyDaemon:
    def __init__(self):
        self.cmdsInterfaces = {}

    def _adminAuth(self, user, passwd):
        raise RuntimeError("permission denied")

    def addCMDsInterface(self, cmdInterfaceClass, category):
        self.cmdsInterfaces.setdefault(category, []).append(cmdInterfaceClass())


class ProcessmanagerFactory:
    """
    """

    def __init__(self):
        self.__jslocation__ = "j.legacy.processmanager"

        self.daemon = DummyDaemon()
        self.basedir = j.sal.fs.joinPaths(j.dirs.base, 'apps', 'processmanager')
        self.redis = j.core.db

    def start(self, acl):

        j.legacy.jumpscripts.loadFromAC(acl)

        self.daemon = j.servers.geventws.getServer(port=4446)  # @todo no longer needed I think, it should not longer be a socket server, lets check first

        # clean old stuff from redis
        j.legacy.redisworker.deleteProcessQueue()

        self.redis.set("processmanager:startuptime", str(int(time.time())))

        self.starttime = j.data.time.getTimeEpoch()

        self.loadCmds()

        self.cmds.jumpscripts.schedule()

        self.daemon.start()

    def _checkIsNFSMounted(self, check=""):
        if check == "":
            check = j.dirs.codeDir
        rc, out = j.sal.process.execute("mount")
        found = False
        for line in out.split("\n"):
            if line.find(check) != -1:
                found = True
        return found

    def restartWorkers(self):
        for queuename in ('default', 'io', 'hypervisor', 'process'):
            j.clients.redisworker.redis.lpush("workers:action:%s" % queuename, "RESTART")

    def getCmdsObject(self, category):
        if self.cmds.has_key(category):
            return self.cmds["category"]
        else:
            raise RuntimeError("Could not find cmds with category:%s" % category)

    def loadCmds(self):
        if self.basedir not in sys.path:
            sys.path.insert(0, self.basedir)
        cmds = j.sal.fs.listFilesInDir(j.sal.fs.joinPaths(self.basedir, "processmanagercmds"), filter="*.py")
        cmds.sort()
        for item in cmds:
            name = j.sal.fs.getBaseName(item).replace(".py", "")
            if name[0] != "_":
                module = importlib.import_module('processmanagercmds.%s' % name)
                classs = getattr(module, name)
                print ("load cmds object:%s" % name)
                tmp = classs(daemon=self.daemon)
                self.daemon.addCMDsInterface(classs, category=tmp._name)

        self.cmds = Dummy()
        # if self.daemon.osis:
        #     self.loadMonitorObjectTypes()

        def sort(item):
            key, cmd = item
            return getattr(cmd, 'ORDER', 10000)

        for key, cmd in sorted(self.daemon.daemon.cmdsInterfaces.iteritems(), key=sort):

            self.cmds.__dict__[key] = cmd
            if hasattr(self.cmds.__dict__[key], "_init"):
                print ("### INIT ###:%s" % key)
                self.cmds.__dict__[key]._init()

    # def loadMonitorObjectTypes(self):
    #     if self.basedir not in sys.path:
    #         sys.path.insert(0, self.basedir)
    #     self.monObjects = Dummy()
    #     for item in j.sal.fs.listFilesInDir(j.sal.fs.joinPaths(self.basedir, "monitoringobjects"), filter="*.py"):
    #         name = j.sal.fs.getBaseName(item).replace(".py", "")
    #         if name[0] != "_":
    #             monmodule = importlib.import_module('monitoringobjects.%s' % name)
    #             classs = getattr(monmodule, name)
    #             print
    #             "load monitoring object:%s" % name
    #             factory = getattr(monmodule, '%sFactory' % name)(self, classs)
    #             self.monObjects.__dict__[name.lower()] = factory

    def getStartupTime(self):
        val = self.redis.get("processmanager:startuptime")
        return int(val)

    def checkStartupOlderThan(self, secago):
        return self.getStartupTime() < int(time.time()) - secago
