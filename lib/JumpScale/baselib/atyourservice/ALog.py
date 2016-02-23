from JumpScale import j

# class Action():
#     def __init__(self,alog,runid,epoch,role,instance,name):
#         self.alog=alog
#         self.runid=int(runid)
#         self.epoch=int(epoch)
#         self.role=role
#         self.instance=instance
#         self.name=name
#         self.cat=cat
#         self.error=False
#         self.done=False
#         self.state={}
#         if new:
#             self._setLog()

#         self.alog.currentActions["%s!%s"%(self.role,self.instance)]=self

#     def _setLog(self):
#         self.alog._append("A | %-10s | %-15s | %-25s | %-15s | %-5s | %s"%(self.epoch,self.role,self.instance,self.name,self.cat,self.state))

#     def setOk(self):
#         self.state="DONE"
#         self._setLog()


#     def getLogs(self):
#         args={"logs":[]}

#         def loghandler(action,lcat,msg,args):
#             if action.key==self.key:
#                 args["logs"].append((lcat,msg))

#         self.alog.process(loghandler=loghandler,args=args)

#         return args["logs"]

#     def getErrors(self):
#         logs=self.getLogs()
#         from IPython import embed
#         print ("DEBUG NOW logs geterrors")
#         embed()


#         return args["logs"]

#     def log(self,msg,cat="",level=0):
#         msg=msg.strip()
#         msg=msg.replace("|","§§")

#         if level!=0:
#             cat="%s %s"%(level,cat)

#         out="L | %11s | %s"%(cat,msg)
#         self.alog._append(out)

#     def error(self,msg):
#         self.log(msg,cat="ERROR",level=0)


#     def __str__(self):
#         return "%-4s | %-10s | %-10s | %-35s |  %-5s | %-10s | %s "%(self.runid,self.epoch,self.role,self.instance,self.cat,self.name,self.state.lower())

#     __repr__=__str__

class LogItem(object):
    """LogItem is the base classe for log lines"""

    def __init__(self, epoch=None):
        super(LogItem, self).__init__()
        if not epoch:
            epoch = j.data.time.getTimeEpoch()
        self.epoch = epoch

    @staticmethod
    def parseLine(line):
        cat, line1 = line.split("|", 1)
        cat = cat.strip()
        if cat == "R":
            epoch, runid, action, hrdtime = line1.split("|")
            return RunLine(runid=int(runid), action=action, hrdtime=hrdtime, epoch=int(epoch))

        if cat == "G":
            epoch, category, githash = [item.strip() for item in line1.split("|", 3)]
            return GitLine(category=category, git_hash=githash, epoch=epoch)

        if cat == "A":
            epoch, servicekey, action, state = [item.strip() for item in line1.split("|")]
            return ActionLine(key=servicekey, action_name=action, state=state, epoch=epoch)

        if cat == "L":
            epoch, level, msg = [item.strip() for item in line1.split("|")]
            try:
                level = int(level)
                return LogLine(msg=msg, level=level, epoch=None)
            except ValueError:
                return LogLine(msg=msg, category=level, epoch=None)

    def __str__(self):
        return repr(self)


class RunLine(LogItem):
    """docstring for """

    def __init__(self, runid, action, hrdtime=None, epoch=None):
        super(RunLine, self).__init__(epoch)
        self.runid = runid
        self.action = action
        if not hrdtime:
            hrdtime = j.data.time.getLocalTimeHR()
        self.hrdtime = hrdtime

    def __repr__(self):
        return "R | %-8s | %-8s | %-10s | %s" % \
            (self.epoch, self.runid, self.action, self.hrdtime)


class ActionLine(LogItem):
    """docstring for """

    def __init__(self, key, action_name, state, epoch=None):
        super(ActionLine, self).__init__(epoch)
        self.key = key
        self.action_name = action_name
        self.state = state

    def __repr__(self):
        return "A | %-8s | %-20s | %-8s | %s" % \
            (self.epoch, self.key, self.action_name, self.state)


class GitLine(LogItem):
    """docstring for """

    def __init__(self, category, git_hash, epoch=None):
        super(GitLine, self).__init__(epoch)
        self.category = category
        self.git_hash = git_hash

    def __repr__(self):
        return "G | %-8s | %-8s | %s" % \
            (self.epoch, self.category, self.git_hash)


class LogLine(LogItem):
    """docstring for """

    def __init__(self, msg, category=None, level=None, epoch=None):
        super(LogLine, self).__init__(epoch)
        self.category = category
        self.level = level
        self.msg = msg

    def __repr__(self):
        if self.category:
            return "L | %-8s | %-8s | %s" % \
                (self.epoch, self.category, self.msg)
        elif self.level:
            return "L | %-8s | %-8s | %s" % \
                (self.epoch, self.level, self.msg)


class ALog():
    """
    actionlog

    format of log is


    RUN
    ===
    R | $epoch | $runid | $action | $hrtime
    A | $epoch | $role!$instance | $actionname | $state
    G | $epoch | $cat   | $githash
    L | $epoch | $level $cat | $msg
    L | $epoch | $cat   | $msg

    R stands for RUN & has unique id
    each action has id

    A stands for action

    L stands for Log

    G stands for GIT action with cat e.g. init, deploy, ...

    multiline messages are possible, they will just reuse their id

    """

    def __init__(self, category):
        if not category.strip():
            raise RuntimeError("category cannot be empty")
        self.category = category
        self.path = j.sal.fs.joinPaths(j.atyourservice.basepath, "alog", "%s.alog" % category)
        j.sal.fs.createDir(j.sal.fs.joinPaths(j.atyourservice.basepath, "alog"))

        self.lastGitRef = {}  # key = action used to log the git hash
        self.lastRunId = 0
        self.lastRunEpoch = 0
        self._git = None

        self.changecache = {}

        if not j.sal.fs.exists(self.path):
            j.sal.fs.createEmptyFile(self.path)
            self.newRun()
        else:
            self.read()

    @property
    def git(self):
        if not self._git:
            self._git = j.clients.git.get()
        return self._git

    def newRun(self, action="unknown"):
        self.lastRunId += 1
        runLine = RunLine(runid=self.lastRunId, action=action)
        self._append(runLine)
        return self.lastRunId

    def newGitCommit(self, action, githash=""):
        if not githash:
            githash = self.git.getCommitRefs()[0][1]
        gitLine = GitLine(category=action, git_hash=githash)
        self._append(gitLine)

    def newAction(self, service, action, state="INIT", logonly=False):
        actionLine = ActionLine(key=service.shortkey, action_name=action, state=state)
        self._append(actionLine, logonly=logonly)

    def log(self, msg, level=5, cat=""):
        for item in msg.strip().splitlines():
            logLine = LogLine(level=level, msg=item)
            self._append(logLine, logonly=True)
            # self._append("L | %-8s | %-8s | %s"%(j.data.time.getTimeEpoch(),level,item),logonly=True)

    def _append(self, logItem, logonly=False):
        item_str = str(logItem)
        if not item_str.strip():
            return

        if not item_str.endswith('\n'):
            item_str += "\n"
        j.sal.fs.writeFile(self.path, item_str, append=True)
        if not logonly:
            self._processLine(logItem=logItem)

    def getLastRef(self, action="install"):
        if action in self.lastGitRef:
            lastref = self.lastGitRef[action]
        else:
            # if action!="init":
            #     lastref=self.getLastRef("init")
            # else:
            lastref = ""
        return lastref

    def getChangedFiles(self,action="install"):
        git=j.clients.git.get()
        changes=git.getChangedFiles(fromref=self.getLastRef(action))
        changes=[item for item in changes if j.do.exists(j.do.joinPaths(git.baseDir,item))]  #we will have to do something for deletes here
        changes.sort()
        return changes

    def getChangedAtYourservices(self, action="install"):
        """
        return (changed,changes)
        changed is list of all changed aysi or ays

        """
        if action in self.changecache:
            return self.changecache[action]

        changed = []
        changes = {}
        for path in self.getChangedFiles(action):
            ttypes = ['services/', 'recipes/', 'servicetemplates/']
            ttype = None
            for t in ttypes:
                i = path.find(t)
                if i != -1:
                    ttype = t
                    break

            if ttype:
                path0 = path.split("%s/" % ttype[:-1], 1)[1]
                basename = j.sal.fs.getBaseName(path0)
                path1 = path0.replace(basename, "").strip("/")
                key = path1.split("/")[-1]

                if ttype == "services":
                    keys = [key]
                else:
                    keys = []
                    for aysi in j.atyourservice.findServices(role=key):
                        keys.append(aysi.shortkey)

                for key in keys:
                    # print ("get changed ays for key:%s"%key)
                    role, instance = key.split("!")
                    aysi = j.atyourservice.getService(role, instance)
                    if basename not in changes:
                        changes[basename] = []
                    changes[basename].append(aysi)
                    if aysi not in changed:
                        changed.append(aysi)

        self.changecache[action] = (changed, changes)

        return changed, changes

    def _processLine(self, logItem):
        if isinstance(logItem, RunLine):
            self.lastRunId = int(logItem.runid)
            self.lastRunEpoch = int(logItem.epoch)
            return

        if isinstance(logItem, GitLine):
            self.lastGitRef[logItem.category] = logItem.git_hash
            return

        if isinstance(logItem, ActionLine):
            role, instance = logItem.key.split("!")
            service = j.atyourservice.getService(role=role, instance=instance)
            service._setAction(name=logItem.action_name, epoch=int(logItem.epoch), state=logItem.state, log=False)
            return

    def removeLastRun(self):
        self.removeRun(self.lastRunId)

    def removeRun(self, id):
        C = j.sal.fs.fileGetContents(self.path)
        path2 = self.path + "_"
        j.sal.fs.createEmptyFile(path2)
        for line in C.splitlines():
            if line.strip() == "" or line.startswith("=="):
                continue
            cat, line1 = line.split("|", 1)
            cat = cat.strip()
            if cat == "R":
                epoch, runid, remaining = line1.split("|", 2)
                if int(runid) == id:
                    # found end
                    j.sal.fs.moveFile(path2, self.path)
                    return

            j.sal.fs.writeFile(path2, line + "\n", append=True)

    def read(self):
        C = j.sal.fs.fileGetContents(self.path)
        for line in C.splitlines():
            if line.strip() == "" or line.startswith("=="):
                continue

            self._processLine(LogItem.parseLine(line))

            # if logmsg!="" or cat=="L":
            #     if cat=="L":
            #         lcat,msg0=line1.split("|",1)
            #         logmsg+="%s\n"%msg0
            #         if msg0.strip()[-1]=="\\":
            #             #go to next line there is enter at end of line
            #             continue

            #     for loghandler in loghandlers:
            #         loghandler(action,lcat,logmsg.strip(),args)  #process log
            #     logmsg=""
            #     lcat=""
