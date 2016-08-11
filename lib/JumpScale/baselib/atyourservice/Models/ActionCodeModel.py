from JumpScale import j

from JumpScale.baselib.atyourservice.ModelBase import ModelBase


class ActionCodeModel(ModelBase):
    """
    Object holding source code from service template actions
    """

    def __init__(self, category='', db=None, key=""):
        self._capnp = j.atyourservice.db.AYSModel.ActionCode
        ModelBase.__init__(self, category=category, db=db, key=key)

    def _post_init(self):
        pass

    def _pre_save(self):
        pass

    def _get_key(self):
        if self.model.guid == "":
            raise j.exceptions.Input(message="guid cannot be empty", level=1, source="", tags="", msgpub="")
        return self.model.guid
