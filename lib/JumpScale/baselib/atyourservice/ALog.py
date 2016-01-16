from JumpScale import j

class Action():
    def __init__(self,alog,runid,epoch,role,instance,name,state="START",new=False):
        self.key="%s_%s"%(runid,role)
        self.alog=alog
        self.runid=int(runid)
        self.epoch=int(epoch)
        self.role=role
        self.instance=instance
        self.name=name
        self.error=False
        self.done=False
        self.state=state
        if new:
            self._setLog()

    def _setLog(self):
        self.alog._append("A | %-10s | %-15s | %-25s | %s | %s"%(self.epoch,self.role,self.instance,self.name,self.state))

    def setOk(self):
        self.state="DONE"
        self._setLog()
        

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
        return "%-4s | %-10s | %-10s | %-35s | %-10s | %s "%(self.runid,self.epoch,self.role,self.instance,self.name,self.state)

    __repr__=__str__

class ALog():
    """
    actionlog

    format of log is
    

    RUN
    ===
    R | $id | $epoch | $hrtime
    A | $id | $epoch | $role  | $instance | $actionname 
    L | $level $cat   | $msg 
    L | $cat   | $msg 

    G | $cat | $epoch | $githash | $hrtime   

    R stands for RUN & has unique id
    each action has id

    A stands for action

    L stands for Log

    G stands for GIT action with cat e.g. init, deploy, ...

    multiline messages are possible, they will just reuse their id

    """
    def __init__(self,category):
        if category.strip()=="":
            raise RuntimeError("category cannot be empty")
        self.category=category
        self.path=j.do.joinPaths(j.atyourservice.basepath,"alog","%s.alog"%category)
        j.sal.fs.createDir(j.do.joinPaths(j.atyourservice.basepath,"alog"))


        self.latest={}  #key = $role!$instance
                        #value = {$actionname:$actionobject}

        self.latestRunId=0
        self.latestActionId={} #key=runid
        # self.currentRunId=0

        self.gitActions={} #key is the aysi action e.g. init or install

        self.gitActionInitLast=""

        self.changecache={}

        if not j.do.exists(self.path):
            j.do.writeFile(self.path,"")
            self.setNewRun()
        else:        
            self.read()

        

    def setNewRun(self):
        self.latestRunId+=1
        self._append("R | %-3s | %-8s |%s"%(self.latestRunId,j.data.time.getTimeEpoch(),j.data.time.getLocalTimeHR()))
        return self.latestRunId

    def setGitCommit(self,action,githash=""):
        if githash=="":
            git=j.clients.git.get()
            githash=git.getCommitRefs()[0][1]
            
        self._append("G | %-3s | %-8s | %s |%s"%(action,j.data.time.getTimeEpoch(),githash,j.data.time.getLocalTimeHR()))

    def setNewAction(self,role,instance,actionname):
        if self.latestRunId==0:
            raise RuntimeError("latestRunId should not be 0.")
        key="%s!%s"%(role.lower().strip(),instance.lower().strip())
        if key not in self.latest:
            self.latest[key]={}
        self.latest[key][actionname]=Action(self,self.latestRunId,j.data.time.getTimeEpoch(),role,instance,actionname,"START",new=True)
        
        return self.latest[key][actionname]

    def _append(self,msg):
        msg=msg.strip()
        if len(msg)==0:
            return
        msg=msg+"\n"
        j.sal.fs.writeFile(self.path, msg, append=True)  

    def getLastRef(self,action="install"):
        if action in self.gitActions:
            lastref=self.gitActions[action][1]
        else:
            lastref=self.gitActionInitLast
        
        # if lastref=="":
        #     raise RuntimeError("could not find lastref for action:%s"%action)
        return lastref

    def getChangedFiles(self,action="install"):
        git=j.clients.git.get()
        changes=git.getChangedFiles(fromref=self.getLastRef(action))
        changes=[item for item in changes if j.do.exists(j.do.joinPaths(git.baseDir,item))]  #we will have to do something for deletes here
        changes.sort()
        return changes

    def getChangedAtYourservices(self,action="install"):
        """
        return (changed,changes)
        changed is list of all changed aysi or ays 

        """
        if action in self.changecache:
            return self.changecache[action]

        changed=[]
        changes={}
        for path in self.getChangedFiles(action):
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
                    # print ("get changed ays for key:%s"%key)
                    aysi=j.atyourservice.getServiceFromKey(key)
                    if basename not in changes:
                        changes[basename]=[]
                    changes[basename].append(aysi)
                    if aysi not in changed:
                        changed.append(aysi)

        self.changecache[action]=(changed,changes)
    
        return changed,changes

    def read(self,actionhandler=None,loghandlers=[],args={}):

        C=j.do.readFile(self.path)

        run = (0,0) #2nd is epoch
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
                # if gitcat!="init":
                #     if not gitcat in self.gitActionInitLast:
                #     self.gitActionInitLast[gitcat]=self.gitActions["init"][1] #hash only
                if gitcat=="init" and self.gitActionInitLast=="":
                    self.gitActionInitLast=githash
                self.gitActions[gitcat]=(epoch,githash)
                continue

            if cat=="A":
                line1.split("|")
                epoch,role,instance,name,state=[item.strip() for item in line1.split("|")]
                action=Action(self,run[0],epoch,role,instance,name=name,state=state)

                if actionhandler!=None:
                    actionhandler(action,args)

                #remember latest action per instance
                key="%s!%s"%(role,instance)
                if key not in self.latest:
                    self.latest[key]={}
                self.latest[key][name]=action

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



        