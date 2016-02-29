
from JumpScale import j
import time
import inspect
import traceback

class Action:    
    def __init__(self, action=None,runid=0,actionRecover=None,args=(),kwargs={},die=True,stdOutput=True,errorOutput=True,retry=1,serviceObj=None,deps=[],key="",selfGeneratorCode="",force=False):
        '''
        self.doc is in doc string of method
        specify recover actions in the description

        name is name of method

        @param name if you want to overrule the name

        @param id is unique id which allows finding back of action
        @param loglevel: Message level
        @param action: python function to execute
        @param actionRecover: link to other action (same as this object but will be used to recover the situation)
        @param args is dict with arguments
        @param serviceObj: service, will be used to get category filled in
        @param isparent, if isparent then when this action changes all actions following will be redone of same runid

        '''

        if key=="" and action==None:
            raise RuntimeError("need to specify key or action")

        self._args=""
        self._kwargs=""
        self._method = None
        self._result=""
        self._stdOutput=stdOutput
        self._errorOutput=errorOutput
        self._state="INIT"
        
        #avoid we can write to it
        self._name=""
        self._path=""
        self._source=""
        self._doc=""

        self._state_show="INIT"        
        self._selfobj=None
        self._key=key
        self._depkeys=[]
        self._deps=[]
        self._actionRecover=""

        self._lastCodeMD5=""
        self._lastArgsMD5=""
        self.stdouterr=""
        self.loglevel = 5
        self.retry=retry
        self.die=die
        self.force=force

        self.traceback=""

        self.runid = str(runid)

        if action!=None:

            self.selfGeneratorCode=selfGeneratorCode

            self.args = args
            self.kwargs= kwargs

            self.serviceObj = serviceObj

            self.method=action        

            if actionRecover!=None:
                self._actionRecover = actionRecover.key

        if key=="":
            if deps!=None:
                deps=[dep for dep in deps if dep!=None]

            if deps!=None and deps!=[]:
                #means they are specified
                self._deps=deps
                self._depkeys=[dep.key for dep in deps ]
            elif deps==None:
                #need to grab last one if it exists
                if j.actions.last!=None:
                    deps=[j.actions.last]
                else:
                    deps=[]
                self._depkeys=[dep.key for dep in deps ]
                self._deps=deps
            else:
                self._deps=deps
                self._depkeys=[dep.key for dep in deps]

            self._load()
        else:
            self._load(True)


        if self.state=="INIT" and key=="":
            #is first time
            self.save(True)

    @property
    def state(self):
        if j.actions.showonly:
            return self._state_show
        else:
            return self._state

    @state.setter
    def state(self,val):
        if j.actions.showonly:
            self._state_show=val
        else:
            self._state=val

    @property
    def deps(self):
        if self._deps==[]:
            for depkey in self._depkeys:
                action=j.actions.actions[depkey]
                self._deps.append(action)
        return self._deps

    def getDepsAll(self):
        res=self._getDepsAll()
        if self in res:
            res.pop(res.index(self))
        return res

    def _getDepsAll(self,res=[]):
        for a in self.deps:
            if a not in res:
                res.append(a)
            res=a._getDepsAll(res)
        return res

    def getWhoDependsOnMe(self):
        res=[]
        for key,action in j.actions.actions.items():
            if self in action.getDepsAll():
                res.append(action)
        return res

    def changeStateWhoDependsOnMe(self,state):
        for action in self.getWhoDependsOnMe():
            action.state=state

    @property
    def model(self):
        model = {}
        model["_name"] = self.name
        model["_key"] = self.key
        model["_doc"] = self.doc
        model["_path"] = self.path
        model["_state"] = self._state
        model["_lastArgsMD5"] = self._lastArgsMD5
        model["_lastCodeMD5"] = self._lastCodeMD5
        model["_depkeys"]=self._depkeys
        model["stdouterr"]=self.stdouterr
        model["_source"]=self._source
        model["_args"]=self._args
        model["_kwargs"]=self._kwargs
        model["_result"]=self._result
        model["selfGeneratorCode"]=self.selfGeneratorCode
        model["runid"] = self.runid
        model["_state_show"] = self._state_show
        model["_actionRecover"] = self._actionRecover
        model["traceback"] = self.traceback
        model["die"] = self.die
        return model

    def _load(self,all=False):
        # print('load key %s' % self.key)
        data = j.core.db.hget("actions.%s" % self.runid, self.key)

        if data != None:
            data2 = j.data.serializer.json.loads(data)

            if all:
                data3=data2
            else:
                toload=["_state","_lastArgsMD5","_lastCodeMD5","_result","traceback","stdouterr"]
                data3={}
                for item in toload:
                    data3[item]=data2[item]

            self.__dict__.update(data3)

            if self._result == "":
                self._result = None

        else:
            if self._key!="":
                raise RuntimeError("could not load action:%s, was not in redis & key specified"%self._name)

    @property
    def actionRecover(self):
        if self._actionRecover==None or  self._actionRecover=="":
            return None
        return j.actions.get(self._actionRecover)

    def check(self):
        if j.data.hash.md5_string(self.source) != self._lastCodeMD5:
            self.state = "SOURCECHANGED"
            self.changeStateWhoDependsOnMe("SOURCEPARENTCHANGED")
            self.save()

        if j.data.hash.md5_string(self._args+self._kwargs) != self._lastArgsMD5:
            self.state = "ARGSCHANGED"
            self.changeStateWhoDependsOnMe("ARGSPARENTCHANGED")
            self.save()

    @property
    def method(self):
        if self.source=="":
            raise RuntimeError("source cannot be empty")
        if self._method == None:
            exec(self.source)
            self._method=eval("%s"%self.name)
        return self._method  

    @method.setter
    def method(self,val):
        source = "".join(inspect.getsourcelines(val)[0])
        if source != "" and source[-1] != "\n":
            source += "\n"
        if source.strip().startswith("@"):
            #decorator needs to be removed (first line)
            source="\n".join(source.split("\n")[1:])            
        self._source=j.data.text.strip(source)
        self._name = source.split("\n")[0].strip().replace("def ", "").split("(")[0].strip()    
        self._path = inspect.getsourcefile(val).replace("//", "/")    
        self._doc=inspect.getdoc(self.method)
        if self._doc==None:
            self._doc=""
        if self._doc!="" and self._doc[-1]!="\n":
            self._doc+="\n"

    @property
    def depsAreOK(self):
        for action in self.deps:
            if action.state!="OK":
                return False
        return True

    @property
    def readyForExecute(self):
        self.check()
        if self.state!="OK" and self.depsAreOK:
            return True
        return False    

    def save(self,checkcode=False):
        if checkcode:
            self._lastArgsMD5 = j.data.hash.md5_string(self._args+self._kwargs)
            self._lastCodeMD5 = j.data.hash.md5_string(self.source)
        j.core.db.hset("actions.%s" % self.runid, self.key, self.modeljson)

    @property
    def key(self):
        if self._key=="":
            extra=""
            key = "%s.%s.%s" % (self.filename,self.name,self._args1line)
            return key
        else:
            return self._key

    @property
    def filename(self):
        return j.sal.fs.getBaseName(self.path)[:-3]

    @property
    def modeljson(self):
        return j.data.serializer.json.dumps(self.model, True, True)

    @property
    def doc(self):
        return self._doc

    @property
    def source(self):
        return self._source

    @property
    def name(self):
        return self._name

    @property
    def result(self):
        if self._result=="" or self._result==None:
            return None
        return j.data.serializer.json.loads(self._result)

    @result.setter
    def result(self,val):
        if val is None:
            self._result = ""
        else:
            self._result = j.data.serializer.json.dumps(val, True, True) 

    @property
    def args(self):
        if self._args == "":
            return ()
        else:
            return j.data.serializer.json.loads(self._args)

    @args.setter
    def args(self,val):
        if val == ():
            self._args = ""
        else:
            self._args = j.data.serializer.json.dumps(val, True, True)     

    @property
    def kwargs(self):
        if self._kwargs == "":
            return {}
        else:
            return j.data.serializer.json.loads(self._kwargs)

    @kwargs.setter
    def kwargs(self,val):
        if val == {}:
            self._kwargs = ""
        else:
            self._kwargs = j.data.serializer.json.dumps(val, True, True)     

    @property
    def _args1line(self):
        out=""
        for arg in self.args:
            out+="%s,"%arg
        out=out.strip(",")
        out+="|"
        for key,arg in self.kwargs.items():
            out+="%s!%s,"%(key,arg)
        out=out.strip(",")
        args=out.strip()
        if len(args)>60:
            args=j.data.hash.md5_string(args)
        return args

    @property
    def path(self):
        return self._path

    @property
    def selfobj(self):
        if self._selfobj!=None:
            return self._selfobj

        if self.selfGeneratorCode!="":
            try:
                l={}
                exec(self.selfGeneratorCode,globals(),l)
                self._selfobj=l["selfobj"]
            except Exception as e:
                self.stdouterr += "SELF OBJ ERROR:\n%s" % e
                self.state = "ERROR"
                raise RuntimeError("%s" % str(self))                        

        return self._selfobj

    def execute(self):
        self.check() #see about changed source code

        if self.force:
            self.state="FORCE"
            print ("FORCE")

        if self.state == "OK":
            print("  * %-20s: %-80s (ALREADY DONE)" % (self.name, self._args1line))
            return

        # if self.state == "ERROR":
        #     print ("ACTION WAS ALREADY IN ERROR:")
        #     raise RuntimeError("%s" % str(self))

        print("  * %-20s: %s" % (self.name, self._args1line))

        if self._stdOutput == False:
            j.tools.console.hideOutput()

        if j.actions.showonly==False:
            rcode = 0
            output = ""
            counter=0
            ok=False
            err=""
            while ok==False and counter<self.retry+1:
                try:
                    if self.selfobj!=None:
                        self.result = self.method(self.selfobj,*self.args,**self.kwargs)
                    else:
                        self.result = self.method(*self.args,**self.kwargs)
                    ok=True
                    rcode=0
                    self.traceback=""
                except Exception as e:
                    for line in traceback.format_stack():
                        if "/IPython/" in line:
                            continue
                        if "JumpScale/tools/actions" in line:
                            continue
                        line=line.strip().strip("' ").strip().replace("File ","")
                        err+="%s\n"%line.strip()
                    err+="ERROR:%s\n"%e
                    self.traceback=err
                    counter+=1
                    time.sleep(0.1)
                    print("  RETRY, ERROR (%s/%s)" % (counter, self.retry))
                    rcode = 1
            
            if self._stdOutput == False:
                j.tools.console.enableOutput()
                self.stdouterr += j.tools.console.getOutput()

    
            if rcode > 0:
                if err!="":
                    self.stdouterr += err
                self.state = "ERROR"
                print(str(self))
                self.save()
                if self.actionRecover != None:
                    self.actionRecover.execute()                
                if self.die:
                    raise RuntimeError("%s" % str(self))
            else:
                self.state = "OK"
            self.save(checkcode=True)
        else:
            rcode=0
            self.state="OK"
            self.save()

        return rcode

    def __str__(self):
        msg=""
        if self.state=="ERROR":
            msg += "***ERROR***\n"
        msg += "action: %-20s runid:%-15s      (%s)\n" % (self.name, self.runid, self.state)
        if self.state=="ERROR":
            msg += "    %s\n"%self.key 
        msg += "    path: %s\n" % self.path
        if self._args != "":
            msg += "ARGS:\n"
            msg += j.data.text.indent(self._args.strip())
            if msg[-1]!="\n":
                msg+="\n"
        if self._kwargs != "":
            msg += "KWARGS:\n"
            msg += j.data.text.indent(self._kwargs.strip())
            if msg[-1]!="\n":
                msg+="\n"
        if self.doc != "":
            msg += "DOC:\n"
            msg += j.data.text.indent(self.doc)
            if msg[-1]!="\n":
                msg+="\n"
        if self.stdouterr != "":
            msg += "OUTPUT:\n%s" % j.data.text.indent(self.stdouterr)
            if msg[-1]!="\n":
                msg+="\n"
        if self.result != None:
            msg += "RESULT:\n%s" % j.data.text.indent(self.result)
        if self.state=="ERROR":
            if self.source != "":
                msg += "SOURCE:\n"
                msg += j.data.text.indent(self.source) + "\n"
            if self.traceback != "":
                msg += "TRACEBACK:\n"
                msg += j.data.text.indent(self.traceback) + "\n"
        if msg[-1]!="\n":
            msg+="\n"
                
            


        return msg

    __repr__ = __str__
