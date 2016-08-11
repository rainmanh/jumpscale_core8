from JumpScale import j

from .ModelBase import ModelBase


class JobModel(ModelBase):
    """
    """

    def __init__(self, category, db, key=""):
        self._capnp = j.atyourservice.db.AYSModel.Job
        ModelBase.__init__(self, category, db, key)

    def _post_init(self):
        self.dbobj.key = j.data.idgenerator.generateGUID()

    def stateChangeNew(self):
        olditems = [item.to_dict() for item in self.dbobj.stateChanges]
        newlist = self.dbobj.init("stateChanges", len(olditems) + 1)
        for i, item in enumerate(olditems):
            newlist[i] = item
        return newlist[-1]

    def log_new(self, **kwargs):
        olditems = [item.to_dict() for item in self.dbobj.logs]
        newlist = self.dbobj.init("logs", len(olditems) + 1)
        for i, item in enumerate(olditems):
            newlist[i] = item
        log = newlist[-1]

        for k, v in kwargs.items():
            if hasattr(log, k):
                setattr(log, k, v)
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
        sc = self.stateChangeNew()
        sc.epoch = j.data.time.getTimeEpoch()
        sc.state = val
        self.dbobj.state = val
