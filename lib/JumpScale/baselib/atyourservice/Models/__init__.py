from JumpScale import j

from .ModelBase import ModelBase


class ServiceModel(ModelBase):
    """
    """

    def __init__(self, category, db, key=""):
        self._capnp = j.atyourservice.db.AYSModel.Service
        ModelBase.__init__(self, category, db, key)
