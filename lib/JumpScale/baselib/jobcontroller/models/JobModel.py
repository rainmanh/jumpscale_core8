from JumpScale import j

ModelBase = j.data.capnp.getModelBaseClass()

import importlib
# import inspect
import msgpack
from collections import OrderedDict

VALID_LOG_CATEGORY = ['out', 'err', 'msg', 'alert', 'errormsg', 'trace']

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
    def find(self, actor="", service="", action="", state="", serviceKey="", fromEpoch=0, toEpoch=9999999999999):
        res = []
        for key in self.list(actor, service, action, state, serviceKey, fromEpoch, toEpoch):
            res.append(self._modelfactory.get(key))
        return res

    def log(self, msg, level=5, category="msg", epoch=None, tags=''):
        """
        category:
              out @0; #std out from executing in console
              err @1; #std err from executing in console
              msg @2; #std log message
              alert @3; #alert e.g. result of error
              errormsg @4; #info from error
              trace @5; #e.g. stacktrace
        """
        if category not in VALID_LOG_CATEGORY:
            raise j.exceptions.Input('category %s is not a valid log category.' % category)

        if epoch is None:
            epoch = j.data.time.getTimeEpoch()
        logitem = self._logObjNew()
        logitem.category = category
        logitem.level = int(level)
        logitem.epoch = epoch
        logitem.log = msg
        logitem.tags = tags
        return logitem

    def _logObjNew(self):
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
        sc = self._stateChangeObjNew()
        sc.epoch = j.data.time.getTimeEpoch()
        sc.state = val
        self.dbobj.lastModDate = sc.epoch
        self.dbobj.state = val

    def _stateChangeObjNew(self):
        olditems = [item.to_dict() for item in self.dbobj.stateChanges]
        newlist = self.dbobj.init("stateChanges", len(olditems) + 1)
        for i, item in enumerate(olditems):
            newlist[i] = item
        return newlist[-1]

    @property
    def args(self):
        if self.dbobj.args == b"":
            return {}
        res = msgpack.loads(self.dbobj.args, encoding='utf-8')
        if res is None:
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

    def objectGet(self):
        """
        returns an Job object created from this model
        """
        return j.core.jobcontroller.newJobFromModel(self)

    @property
    def actionMethod(self):
        """
        is python method which can be executed
        """
        if self.source == "":
            raise j.exceptions.RuntimeError("source cannot be empty")
        if self._method is None:
            # j.sal.fs.changeDir(basepath)
            loader = importlib.machinery.SourceFileLoader(self.name, self.sourceToExecutePath)
            handle = loader.load_module(self.name)
            self._method = eval("handle.%s" % self.name)

        return self._method

    # @actionMethod.setter
    # def actionMethod(self, val):
    #     """
    #     will inspect the method
    #     """
    #
    #     from IPython import embed
    #     print("DEBUG NOW actionMethod")
    #     embed()
    #     raise RuntimeError("stop debug here")

    @property
    def dictFiltered(self):
        ddict = self.dbobj.to_dict()
        to_filter = ['args', 'result', 'profileData']
        for key in to_filter:
            if key in ddict:
                del ddict[key]
        return ddict

    def __repr__(self):
        out = self.dictJson + "\n"
        if self.dbobj.args not in ["", b""]:
            out += "args:\n"
            out += self.argsJons
        return out

    __str__ = __repr__
