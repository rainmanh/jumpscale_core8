from JumpScale import j
from JumpScale.baselib.atyourservice.models.ModelBase import ModelBase
import importlib
import inspect


class JobModel(ModelBase):
    """
    """

    def __init__(self, category, db, index, key=""):
        self._capnp = j.atyourservice.db.AYSModel.Job
        ModelBase.__init__(self, category, db, index, key)

    @classmethod
    def list(self, actor="", service="", action="", state="", fromEpoch=0, toEpoch=999999999, returnIndex=False):
        if actor == "":
            actor = ".*"
        if service == "":
            service = ".*"
        if action == "":
            action = ".*"
        if state == "":
            state = ".*"
        epoch = ".*"
        regex = "%s:%s:%s:%s:%s" % (actor, service, action, state, epoch)
        res0 = j.atyourservice.db.job._index.list(regex, returnIndex=True)
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
        ind = "%s:%s:%s:%s:%s" % (self.dbobj.actorName, self.dbobj.serviceName,
                                  self.dbobj.actionName, self.dbobj.state, self.dbobj.lastModDate)
        j.atyourservice.db.job._index.index({ind: self.dbobj._get_key()})

    @classmethod
    def find(self, actor="", service="", action="", state="", fromEpoch=0, toEpoch=999999999):
        res = []
        for key in self.list(actor, service, action, state, fromEpoch, toEpoch):
            res.append(j.atyourservice.db.job.get(key))
        return res

    def _post_init(self):
        self.dbobj.key = j.data.idgenerator.generateGUID()

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
        self.dbobj.state = val

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
        source = "".join(inspect.getsourcelines(val)[0])
        if source != "" and source[-1] != "\n":
            source += "\n"
        if source.strip().startswith("@"):
            # decorator needs to be removed (first line)
            source = "\n".join(source.split("\n")[1:])
        source = j.data.text.strip(source)
        # self._name = source.split("\n")[0].strip().replace("def ", "").split("(")[0].strip()
        # self._path = inspect.getsourcefile(val).replace("//", "/")
        # self._doc=inspect.getdoc(self.method)
        # if self._doc==None:
        #     self._doc=""
        # if self._doc!="" and self._doc[-1]!="\n":
        #     self._doc+="\n"
        from IPython import embed
        print("DEBUG NOW actionMethod")
        embed()
        raise RuntimeError("stop debug here")

    @property
    def source(self):
        if self._source is None:
            self._source = self.runstep.run.db.get_dedupe(
                "source", self.model["source"]).decode()
        return self._source
