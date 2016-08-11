from JumpScale import j
from .ModelBase import ModelBase
import importlib


class JobModel(ModelBase):
    """
    """

    def __init__(self, category, db, key=""):
        self._capnp = j.atyourservice.db.AYSModel.Job
        ModelBase.__init__(self, category, db, key)

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
    def method(self):
        if self.source == "":
            raise j.exceptions.RuntimeError("source cannot be empty")
        if self._method == None:
            # j.sal.fs.changeDir(basepath)
            loader = importlib.machinery.SourceFileLoader(self.name, self.sourceToExecutePath)
            handle = loader.load_module(self.name)
            self._method = eval("handle.%s" % self.name)

        return self._method

    @property
    def source(self):
        if self._source is None:
            self._source = self.runstep.run.db.get_dedupe(
                "source", self.model["source"]).decode()
        return self._source
