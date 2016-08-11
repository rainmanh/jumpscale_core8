from JumpScale import j

from ModelBase import ModelBase


class JobModel(ModelBase):
    """
    """

    def __init__(self, category, db, key=""):
        self._capnp = j.atyourservice.db.AYSModel.Job
        ModelBase.__init__(self, category, db, key)

    def _post_init(self):
        self.dbobj.init_resizable_list('logs')
        self.dbobj.init_resizable_list('stateChanges')
        self.dbobj.key = j.data.idgenerator.generateGUID()

    def _pre_save(self):
        # need to call finish on DynamicResizableListBuilder to prevent leaks
        for builder in [self.dbobj.logs, self.dbobj.stateChanges]:
            if builder is not None:
                builder.finish()
