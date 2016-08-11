from JumpScale import j

from ModelBase import ModelBase


class RunModel(ModelBase):
    """
    is state object for Run
    """

    def __init__(self, category, db, key=""):
        self._capnp = j.atyourservice.db.AYSModel.Run
        ModelBase.__init__(self, category, db, key)

    def _post_init(self):
        # self.db.parent = j.atyourservice.AYSModel.actor.actorPointer.new_message()  # TODO
        self._steps = self.dbobj.init_resizable_list('steps')

    def _pre_save(self):
        # need to call finish on DynamicResizableListBuilder to prevent leaks
        for builder in [self._actions_templates, self._producers, self._recurringTemplate]:
            if builder is not None:
                builder.finish()

    def _get_key(self):
        if self.dbobj.name == "":
            raise j.exceptions.Input(message="name cannot be empty", level=1, source="", tags="", msgpub="")
        return self.dbobj.name

    # def __repr__(self):
    #     out = ""
    #     for item in self.methodslist:
    #         out += "%s\n" % item
    #     return out

    # __str__ = __repr__
