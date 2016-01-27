
from JumpScale import j
import time
import inspect

class Action:    
    def __init__(self, action,runid=0,actionRecover=None,args={},die=True,stdOutput=True,errorOutput=True,retry=1,serviceObj=None,id=0,name=""):
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

        '''
        self.serviceObj = serviceObj
        self.runid = str(runid)
        self.method = action
        self.actionRecover = actionRecover
        self.args = args
        self.loglevel = 5
        self.retry=retry
        self._stdOutput=stdOutput
        self._errorOutput=errorOutput
        self.state="INIT"
        self.die=die
        self.result=None

        self._name=name
        self._path=""
        self._source=""
        self._doc=""
        self._argsdoc=""
        self.stdouterr=""
        self._lastCodeMD5=""
        self._lastArgsMD5=""
        self.id=int(id)

        self._load()

    @property
    def model(self):
        model = {}
        model["_name"] = self.name
        model["_doc"] = self.doc
        model["_path"] = self.path
        model["id"] = self.id
        model["state"] = self.state
        model["_lastArgsMD5"] = self._lastArgsMD5
        model["_lastCodeMD5"] = self._lastCodeMD5
        if self.result is None:
            model["_result"] = ""
        else:
            try:
                model["_result"] = j.data.serializer.json.dumps(self.result, True, True)
            except:
                pass
        model["stdouterr"] = self.stdouterr
        model["runid"] = self.runid
        return model

    def _load(self):
        key = "%s.%s" % (self.id, self.name)
        print('load key %s' % key)
        data = j.core.db.hget("actions.%s" % self.runid, key)

        if data != None:
            data2 = j.data.serializer.json.loads(data)
            self.__dict__.update(data2)

            keys = j.core.db.hkeys("actions.%s" % self.runid)
            keys.sort()
            for key in keys:
                key=key.decode()
                nameinredis=key.split(".")[1]
                idinredis=int(key.split(".")[0])
                if nameinredis==self.name:
                    if idinredis!=self.id:
                        self.removeActionsStartingWithMe()
                        data2["state"] = "CHANGED"

            if self._result == "":
                self._result = None

            if j.data.hash.md5_string(self.source) != self._lastCodeMD5:
                self.state = "SOURCECHANGED"
                self.removeActionsStartingWithMe()

            if j.data.hash.md5_string(self.argsjson) != self._lastArgsMD5:
                self.state = "ARGSCHANGED"
                self.removeActionsStartingWithMe()

    def removeActionsStartingWithMe(self):
        """
        walk over all actions in redis remove myself and all above
        """
        keys = j.core.db.hkeys("actions.%s" % self.runid)
        keys.sort()
        for key in keys:
            key = key.decode()
            idinredis = int(key.split(".")[0])
            if idinredis >= self.id:
                print('########### delete############# %s' % self.name)
                print('########### delete %s' % key)
                j.core.db.hdel("actions.%s" % self.runid, key)

    def save(self):
        key = "%s.%s" % (self.id, self.name)
        self._lastArgsMD5 = j.data.hash.md5_string(self.argsjson)
        self._lastCodeMD5 = j.data.hash.md5_string(self.source)
        j.core.db.hset("actions.%s" % self.runid, key, self.modeljson)

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
        return self._source

    @property
    def name(self):
        if self._name == "":
            self._name = self.source.split("\n")[0].strip().replace("def ", "").split("(")[0].strip()
        return self._name

    @property
    def argsjson(self):
        if self._argsdoc == "":

            if self.args != {}:

                args2 = {}
                if not j.data.types.dict.check(self.args):
                    raise RuntimeError("args should be dict")
                for key, val in self.args.items():
                    try:
                        val2 = str(val)
                    except:
                        val2 = "UNDEFINED"
                    args2[key] = val2

                out = j.data.serializer.json.dumps(args2, True, True)
                self._argsdoc = ""
                for line in out.split("\n"):
                    if line.strip() == "" or line.strip()in ["{", "}"]:
                        continue
                    self._argsdoc += "%s\n" % line

        return self._argsdoc

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

        if self.state == "OK":
            print("* %-20s: %-80s (ALREADY DONE)" % (self.name, self._args1line))
            return

        print("* %-20s: %s" % (self.name, self._args1line))

        if self._stdOutput == False:
            j.tools.console.hideOutput()

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
            msg += j.data.text.indent(self.argsjson)
        if self.doc != "":
            msg += "DOC:\n"
            msg += j.data.text.indent(self.doc)

        if self.stdouterr != "":
            msg += "\nOUTPUT:\n%s" % j.data.text.indent(self.stdouterr)
        if self.result != None:
            msg += "\nRESULT:\n%s" % j.data.text.indent(j.data.serializer.json.dumps(self.result, True, True))
        return msg

    __repr__ = __str__
