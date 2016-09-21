from JumpScale import j

ModelBase = j.data.capnp.getModelBaseClass()

import importlib
# import inspect
import msgpack
from collections import OrderedDict


class JobModel(ModelBase):
    """
    """

    @classmethod
    def list(self, actor="", service="", action="", state="", serviceKey="", fromEpoch=0, toEpoch=9999999999999, returnIndex=False):
        if actor == "":
            actor = ".*"
        if service == "":
            service = ".*"
        if action == "":
            action = ".*"
        if state == "":
            state = ".*"
        if serviceKey == "":
            serviceKey = ".*"
        epoch = ".*"
        regex = "%s:%s:%s:%s:%s:%s" % (actor, service, action, state, serviceKey, epoch)
        res0 = self._index.list(regex, returnIndex=True)
        res1 = []
        for index, key in res0:
            epoch = int(index.split(":")[-1])
            if fromEpoch < epoch and epoch < toEpoch:
                if returnIndex:
                    res1.append((index, key))
                else:
                    res1.append(key)
        return res1

    def index(self):
        # put indexes in db as specified
        ind = "%s:%s:%s:%s:%s:%s" % (self.dbobj.actorName, self.dbobj.serviceName,
                                     self.dbobj.actionName, self.dbobj.state, self.dbobj.serviceKey, self.dbobj.lastModDate)
        self._index.index({ind: self.key})

    @classmethod
    def find(self, actor="", service="", action="", state="", serviceKey="", fromEpoch=0, toEpoch=999999999):
        res = []
        for key in self.list(actor, service, action, state, serviceKey, fromEpoch, toEpoch):
            res.append(self._modelfactory.get(key))
        return res

    def stateChangeObjNew(self):
        olditems = [item.to_dict() for item in self.dbobj.stateChanges]
        newlist = self.dbobj.init("stateChanges", len(olditems) + 1)
        for i, item in enumerate(olditems):
            newlist[i] = item
        return newlist[-1]

    def log(self, msg, level=5, category="msg", epoch=None):
        """
        category:
              out @0; #std out from executing in console
              err @1; #std err from executing in console
              msg @2; #std log message
              alert @3; #alert e.g. result of error
              errormsg @4; #info from error
              trace @5; #e.g. stacktrace
        """
        if epoch is None:
            epoch = j.data.time.getTimeEpoch()
        logitem = self.logObjNew()
        logitem.category = category
        logitem.level = int(level)
        logitem.epoch = epoch
        logitem.msg = msg

    def logObjNew(self):
        # for logs not very fast but lets go with this for now
        olditems = [item.to_dict() for item in self.dbobj.logs]
        newlist = self.dbobj.init("logs", len(olditems) + 1)
        for i, item in enumerate(olditems):
            newlist[i] = item
        log = newlist[-1]
        return log

    @property
    def state(self):
        return self.dbobj.state

    @state.setter
    def state(self, val):
        """
          enum State {
              new @0;
              running @1;
              ok @2;
              error @3;
              abort @4;
          }
        """
        sc = self.stateChangeObjNew()
        sc.epoch = j.data.time.getTimeEpoch()
        sc.state = val
        self.dbobj.lastModDate = sc.epoch
        self.dbobj.state = val

    @property
    def args(self):
        if self.dbobj.args == b"":
            return {}
        res = msgpack.loads(self.dbobj.args, encoding='utf-8')
        if res == None:
            res = {}
        return res

    @property
    def argsJons(self):
        ddict2 = OrderedDict(self.args)
        return j.data.serializer.json.dumps(ddict2, sort_keys=True, indent=True)

    @args.setter
    def args(self, val):
        args = msgpack.dumps(val)
        self.dbobj.args = args

    @property
    def result(self):
        if self.dbobj.result == b"":
            return {}
        return msgpack.loads(self.dbobj.result, encoding='utf-8')

    @property
    def resultJons(self):
        ddict2 = OrderedDict(self.result)
        return j.data.serializer.json.dumps(ddict2, sort_keys=True, indent=True)

    @args.setter
    def result(self, val):
        result = msgpack.dumps(val)
        self.dbobj.result = result

    @property
    def actioncodeObj(self):
        from IPython import embed
        print("DEBUG NOW actioncodeobj")
        embed()
        raise RuntimeError("stop debug here")

    @property
    def actionMethod(self):
        """
        is python method which can be executed
        """
        if self.source == "":
            raise j.exceptions.RuntimeError("source cannot be empty")
        if self._method == None:
            # j.sal.fs.changeDir(basepath)
            loader = importlib.machinery.SourceFileLoader(self.name, self.sourceToExecutePath)
            handle = loader.load_module(self.name)
            self._method = eval("handle.%s" % self.name)

        return self._method

    @actionMethod.setter
    def actionMethod(self, val):
        """
        will inspect the method
        """

        from IPython import embed
        print("DEBUG NOW actionMethod")
        embed()
        raise RuntimeError("stop debug here")

    @property
    def source(self):
        if self._source is None:
            self._source = self.runstep.run.db.get_dedupe(
                "source", self.model["source"])
        return self._source

    @property
    def dictFiltered(self):
        ddict = self.dbobj.to_dict()
        if "args" in ddict:
            ddict.pop("args")
        return ddict

    def __repr__(self):
        out = self.dictJson + "\n"
        if self.dbobj.args not in ["", b""]:
            out += "args:\n"
            out += self.argsJons
        return out

    __str__ = __repr__
