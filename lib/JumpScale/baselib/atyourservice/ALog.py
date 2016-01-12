from JumpScale import j

class Action():
    def __init(self,alog,runid,epoch,actionid,role,instance,name,result,new=True):
        self.key="%s_%s"%(runid,actionid)
        self.alog=alog
        self.runid=int(runid)
        self.epoch=int(epoch)
        self.actionid=int(actionid)
        self.role=role
        self.instance=instance
        self.name=name
        self.error=False

        if new:
            self.alog._append("A | %-3s | %-8s | %-25s | %s"%(self.actionid,role,instance,name))

    def getLogs(self):
        args={"logs":[]}

        def loghandler(action,lcat,msg,args):
            if action.key==self.key:
                args["logs"].append((lcat,msg))

        self.alog.process(loghandler=loghandler,args=args)

        return args["logs"]

    def getErrors(self):
        logs=self.getLogs()
        from IPython import embed
        print ("DEBUG NOW logs geterrors")
        embed()
        


        return args["logs"]

    def log(self,msg,cat="",level=0):
        msg=msg.strip()
        msg=msg.replace("|","§§")

        if level!=0:
            cat="%s %s"%(level,cat)

        out="L | %15s | %s"%(cat,msg)
        self.alog._append(out)

    def error(self,msg):
        self.log(msg,cat="ERROR",level=0)


    def __str__(self):
        return "%-4s | %-10s | %-4s | %-10s | %-35s | %-10s | %s "%(self.runid,self.epoch,self.actionid,self.role,self.instance,self.name,self.result)

    __repr__=__str__

class ALog():
    """
    actionlog

    format of log is
    

    RUN
    ===
    R | $id | $epoch | $hrtime
    A | $id | $role  | $instance | $actionname 
    L | $level $cat   | $msg 
    L | $cat   | $msg 

    G | $cat | $epoch | $githash | $hrtime   

    R stands for RUN & has unique id
    each action has id

    A stands for action

    L stands for Log

    G stands for GIT action with cat e.g. init, ...

    multiline messages are possible, they will just reuse their id

    """
    def __init__(self,category):
        if category.strip()=="":
            raise RuntimeError("category cannot be empty")
        self.category=category
        self.path=j.do.joinPaths(j.atyourservice.basepath,"alog","%s.log"%category)
        j.sal.fs.createDir(j.do.joinPaths(j.atyourservice.basepath,"alog"))

        if not j.do.exists(self.path):
            j.do.writeFile(self.path,"")

        self.latest={}  #key = $role!$instance
                        #value = {$actionname:$actionobject}

        self.latestRunId=0
        self.latestActionId={} #key=runid
        self.currentRunId=0

        self.gitActions={} #key is the git category e.g. init

        self.gitActionInitLast=""

        self.read()

        self.changecache={}

    def getNewRun(self):
        self.currentRunId+=1
        self._append("R | %-3s | %-8s |%s"%(self.currentRunId,j.data.time.getTimeEpoch(),j.data.time.getLocalTimeHR()))
        return self.currentRunId

    def setGitCommit(self,category,githash=""):
        if githash=="":
            git=j.clients.git.get()
            githash=git.getCommitRefs()[0][1]
            
        self._append("G | %-3s | %-8s | %s |%s"%(category,j.data.time.getTimeEpoch(),githash,j.data.time.getLocalTimeHR()))

    def _getNewActionID(self):
        if self.currentRunId not in self.latestActionId:
            self.latestActionId[self.currentRunId]=0
        self.latestActionId[self.currentRunId]+=1
        return self.latestActionId[self.currentRunId]

    def getNewAction(self,role,instance,actionname):
        if self.currentRunId==0:
            raise RuntimeError("currentRunId should not be 0.")
        key="%s!%s"%(role.lower().strip(),instance.lower().strip())
        if key not in self.latest:
            self.latest[key]={}
        self.latest[key][actionname]=Action(self,runid=self.currentRunId,epoch=j.data.time.getTimeEpoch(),\
                actionid=self._getNewActionID(),role=role,instance=instance,name=actionname)
        return self.latest[key][actionname]

    def _append(self,msg):
        msg=msg.strip()
        if len(msg)==0:
            return
        msg=msg+"\n"
        j.sal.fs.writeFile(self.path, msg, append=True)  

    def getChangedFiles(self,category="deploy"):
        if category in self.gitActions:
            lastref=self.gitActions[category]
        else:
            lastref=self.gitActionInitLast
        if lastref=="":
            raise RuntimeError("could not define lastref")
        git=j.clients.git.get()
        return git.getChangedFiles(fromref=lastref)

    def getChangedAtYourservices(self,category="deploy"):
        """
        return (changed,changes)
        changed is list of all changed aysi or ays 

        """
        if category in self.changecache:
            return self.changecache[category]

        changed=[]
        changes={}
        for path in self.getChangedFiles(category):
            if path.find("/services/")!=-1 or path.find("/recipes/")!=-1:
                if path.find("/services/")!=-1:
                    ttype="services"
                else:
                    ttype="recipes"

                path0=path.split("/%s/"%ttype,1)[1]
                basename=j.do.getBaseName(path0)
                path1=path0.replace(basename,"").strip("/")
                key=path1.split("/")[-1]

                if ttype=="services":
                    keys=[key]
                else:
                    keys=[]
                    for aysi in j.atyourservice.findServices(role=key):
                        keys.append(aysi.key)
                    
                for key in keys:
                    aysi=j.atyourservice.getServiceFromKey(key)
                    if basename not in changes:
                        changes[basename]=[]
                    changes[basename].append(aysi)
                    if aysi not in changed:
                        changed.append(aysi)

        self.changecache[category]=(changed,changes)
    
        return changed,changes

    def read(self,actionhandler=None,loghandlers=[],args={}):

        C=j.do.readFile(self.path)

        run = (0,0)
        for line in C.split("\n"):

            if line.strip()=="RUN" or line.strip()=="" or line.startswith("=="):
                continue

            cat,line1=line.split("|",1)
            cat=cat.strip()
            if cat=="R":
                id,epoch,remaining=line1.split("|",2)
                run=(int(id),int(epoch))

                if run[0]>self.latestRunId:
                    self.latestRunId=run[0]

                continue

            if cat =="G":
                gitcat,epoch,githash,remaining=[item.strip() for item in line1.split("|",3)]
                if gitcat!="init":
                    self.gitActionInitLast=self.gitActions["init"]
                if gitcat=="init" and self.gitActionInitLast=="":
                    self.gitActionInitLast=githash
                self.gitActions[gitcat]=(epoch,githash)
                continue

            if cat=="A":
                line1.split("|")
                id,role,instance,name=[item.strip() for item in d.split("|")]
                action=Action(self,run[0],run[1],role,instance,name,new=False)

                if actionhandler!=None:
                    actionhandler(action,args)

                #remember latest action per instance
                key="%s!%s"%(role,instance)
                if key not in self.latest:
                    self.latest[key]={}
                self.latest[key][name]=action

                if action.key not in self.latestActionId:
                    self.latestActionId[action.key]=0
                if action.id>self.latestActionId[action.key]:
                    self.latestActionId[action.key]=action.id

                logmsg=""
                lcat=""

                continue


            if logmsg!="" or cat=="L":
                if cat=="L":
                    lcat,msg0=line1.split("|",1)
                    logmsg+="%s\n"%msg0
                    if msg0.strip()[-1]=="\\":
                        #go to next line there is enter at end of line
                        continue

                for loghandler in loghandlers:
                    loghandler(action,lcat,logmsg.strip(),args)  #process log
                logmsg=""
                lcat=""



        