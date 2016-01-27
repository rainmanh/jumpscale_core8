
from JumpScale import j
import time
import inspect

class Action:    
    def __init__(self, action=None,runid=0,actionRecover=None,args={},die=True,stdOutput=True,errorOutput=True,retry=1,serviceObj=None,deps=[],key=""):
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
        self.serviceObj = serviceObj
        self.runid = str(runid)
        self._method = action
        self.actionRecover = actionRecover
        self._args = args
        self.loglevel = 5
        self.retry=retry
        self._stdOutput=stdOutput
        self._errorOutput=errorOutput
        self._state="INIT"
        self.die=die
        self._result=""
        self.result={}
        self._name=""
        self._path=""
        self._source=""
        self._doc=""
        self._argsjson=""
        self.stdouterr=""
        self._lastCodeMD5=""
        self._lastArgsMD5=""
        self._state_show="INIT"

        self._key=key

        self._depkeys=[]
        self._deps=[]

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
    def args(self):
        if self._args=={}:
            if self._argsjson!="":
                self._args=j.data.serializer.json.loads(self.argsjson)
        return self._args

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
        model["_argsjson"]=self._argsjson
        model["runid"] = self.runid
        model["_state_show"] = self._state_show

        if self.result is None:
            model["_result"] = ""
        else:
            try:
                model["_result"] = j.data.serializer.json.dumps(self.result, True, True)
            except:
                pass
        return model

    def _load(self,all=False):
        # print('load key %s' % self.key)
        data = j.core.db.hget("actions.%s" % self.runid, self.key)

        if data != None:
            data2 = j.data.serializer.json.loads(data)

            if all:
                data3=data2
            else:
                toload=["_state","_lastArgsMD5","_lastCodeMD5","_result"]
                data3={}
                for item in toload:
                    data3[item]=data2[item]

            self.__dict__.update(data3)

            if self._result == "":
                self._result = None

        else:
            if self._key!="":
                raise RuntimeError("could not load action:%s, was not in redis & key specified"%self._name)


    def check(self):
        if j.data.hash.md5_string(self.source) != self._lastCodeMD5:
            self.state = "SOURCECHANGED"
            self.changeStateWhoDependsOnMe("SOURCEPARENTCHANGED")
            self.save()

        if j.data.hash.md5_string(self.argsjson) != self._lastArgsMD5:
            self.state = "ARGSCHANGED"
            self.changeStateWhoDependsOnMe("ARGSPARENTCHANGED")
            self.save()



    @property
    def method(self):
        if self._method == None:
            exec(self.source)
            self._method=eval("%s"%self.name)
        return self._method  

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
            self._lastArgsMD5 = j.data.hash.md5_string(self.argsjson)
            self._lastCodeMD5 = j.data.hash.md5_string(self.source)
        j.core.db.hset("actions.%s" % self.runid, self.key, self.modeljson)

    @property
    def key(self):
        if self._key=="":
            key = "%s.%s" % (self.name,self._args1line)
            return key
        else:
            return self._key

    @property
    def modeljson(self):
        return j.data.serializer.json.dumps(self.model, True, True)

    @property
    def doc(self):
        if self._doc=="":
            self._doc=inspect.getdoc(self.method)
            if self._doc==None:
                self._doc=""
            if self._doc!="" and self._doc[-1]!="\n":
                self._doc+="\n"
        return self._doc

    @property
    def source(self):
        if self._source == "":
            self._source = "".join(inspect.getsourcelines(self.method)[0])
            if self._source != "" and self._source[-1] != "\n":
                self._source += "\n"
            self._source=j.data.text.strip(self._source)
        return self._source

    @property
    def name(self):
        if self._name == "":
            self._name = self.source.split("\n")[0].strip().replace("def ", "").split("(")[0].strip()
        return self._name

    @property
    def argsjson(self):
        if self._argsjson == "":
            args2 = {}
            if not j.data.types.dict.check(self.args):
                raise RuntimeError("args should be dict")
            for key, val in self.args.items():
                try:
                    j.data.serializer.json.dumps(val)
                    #is just a check to see if json serializer will work
                    val2 = val
                except:
                    val2 = "UNDEFINED"
                args2[key] = val2

            out = j.data.serializer.json.dumps(args2, True, True)
            self._argsjson =out
        return self._argsjson

    @property
    def _args1line(self):
        args = self.argsjson.replace("\n", "")
        args = args.replace("'", "")
        args = args.replace("\"", "")
        args = args.replace("{", "")
        args = args.replace("}", ",")
        args = args.replace(",,", ",")
        args = args.replace(" ", "")
        return args

    @property
    def path(self):
        if self._path == "":
            self._path = inspect.getsourcefile(self.method).replace("//", "/")
        return self._path



    def execute(self):
        self.check()
        if self.state == "OK":
            print("  * %-20s: %-80s (ALREADY DONE)" % (self.name, self._args1line))
            return

        print("  * %-20s: %s" % (self.name, self._args1line))

        if self._stdOutput == False:
            j.tools.console.hideOutput()

        if j.actions.showonly==False:
            rcode = 0
            output = ""
            for i in range(self.retry + 1):
                try:
                    self.result = self.method(**self.args)
                except Exception as e:
                    if self.retry > 1 and i < self.retry:
                        time.sleep(0.1)
                        print("  RETRY, ERROR (%s/%s)" % (i + 1, self.retry))
                        continue
                    rcode = 1
                    self.stdouterr += "ERROR:\n%s" % e
                break
            if self._stdOutput == False:
                j.tools.console.enableOutput()
                self.stdouterr += j.tools.console.getOutput()
            if rcode > 0:
                self.state = "ERROR"
                print(self.errormsg)
                if self.actionRecover != None:
                    self.actionRecover.execute()
                self.save()
                if self.die:
                    raise RuntimeError("%s" % self.errormsg)
            else:
                self.state = "OK"
            self.save(checkcode=True)
        else:
            rcode=0
            self.state="OK"
            self.save()

        return rcode

    @property
    def errormsg(self):
        if self.state == "ERROR":
            msg = "***ERROR***\n"
            msg += str(self)
            if self.source != "":
                msg += "SOURCE:\n"
                msg += j.data.text.indent(self.source) + "\n"
            return msg
        return ""

    def __str__(self):
        msg = "action: %-20s runid:%-15s      (%s)\n" % (self.name, self.runid, self.state)
        msg += "    path: %s\n" % self.path
        if self.argsjson != "":
            msg += "ARGS:\n"
            msg += j.data.text.indent(self.argsjson.strip())
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
            msg += "RESULT:\n%s" % j.data.text.indent(j.data.serializer.json.dumps(self.result, True, True))
        if msg[-1]!="\n":
            msg+="\n"
        return msg

    __repr__ = __str__