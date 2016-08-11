from JumpScale import j

from JumpScale.baselib.atyourservice.ModelBase import ModelBase


class ActorModel(ModelBase):
    """
    Model Class for an Actor object
    """

    def __init__(self, actor, category="", db=None, key=""):
        self._capnp = j.atyourservice.db.AYSModel.Actor
        self.actor = actor
        self._actions_templates = None
        self._actions_actor = None
        self._producers = None
        self._recurringTemplate = None
        self._changes = {}

        ModelBase.__init__(self, category, db, key)

    @property
    def methods_service_templates(self):
        methods = {}
        for action_code in self.dbobj.actionsServicesTemplate:
            methods[action_code.name] = action_code.actionCodeKey
        return methods
        # for action_code in self._actions_templates:
        #     methods[action_code.name] = action_code.actionCodeKey

    @property
    def methods_actor(self):
        methods = {}
        for action_code in self.dbobj.actionsActor:
            methods[action_code.name] = action_code.actionCodeKey
        return methods

    @property
    def methods_service_list(self):
        """
        sorted methods of the services managed by this actor
        """
        if self._methodsList == []:
            keys = sorted([item for item in self.methods_service_templates.keys()])
            for key in keys:
                self._methodsList.append(self.methods[key])
        return self._methodsList

    @property
    def methods_actor_list(self):
        """
        Sorted methods of the actor
        """
        if self._methodsList == []:
            keys = sorted([item for item in self.methods_actor.keys()])
            for key in keys:
                self._methodsList.append(self.methods[key])
        return self._methodsList

    def _post_init(self):
        # self.db.parent = j.atyourservice.AYSModel.actor.actorPointer.new_message()  # TODO
        # self._producers = self.dbobj.init_resizable_list('producers')
        self._actions_templates = self.dbobj.init_resizable_list('actionsServicesTemplate')
        self._actions_actor = self.dbobj.init_resizable_list('actionsActor')
        # self._recurringTemplate = self.dbobj.init_resizable_list('recurringTemplate')
        self.dbobj.name = self.actor.name
        self.dbobj.key = j.data.idgenerator.generateGUID()
        self.dbobj.ownerKey = j.data.idgenerator.generateGUID()

    def _pre_save(self):
        # if self.isChanged:
        #     new_list = self.dbobj.init('actionsServicesTemplate', len(self._actions_templates))
        #     for i, action in enumerate(self._actions_templates):
        #         new_list[i] = action

        # need to call finish on DynamicResizableListBuilder to prevent leaks
        for builder in [self._actions_templates, self._producers, self._recurringTemplate, self._actions_actor]:
            if builder is not None:
                builder.finish()

    def _get_key(self):
        if self.dbobj.name == "":
            raise j.exceptions.Input(message="name cannot be empty", level=1, source="", tags="", msgpub="")
        return self.dbobj.name

    def addMethod(self, name="", source="", isDefaultMethod=False):
        if source != "":
            if name in ["input", "init"] and source.find("$(") != -1:
                raise j.exceptions.Input(
                    "Action method:%s should not have template variable '$(...' in sourcecode for init or input method." % self)

            guid = j.data.hash.blake2_string(self.actor.name + source)

            # if new method or new code
            if not j.atyourservice.db.action_code.exists(guid):
                # create new actionCode model
                action_code = j.atyourservice.db.action_code.new()
                action_code.model.guid = guid
                action_code.model.name = name
                action_code.model.actorName = self.actor.name
                action_code.model.code = source
                action_code.model.lastModDate = j.data.time.epoch
                # save action_code into db
                action_code.save()

                # put pointer to actionCode to actor model
                action = self._actions_templates.add()
                # action = self._capnp.Action.new_message()
                action.name = name
                action.actionCodeKey = guid
                # self._actions_templates.append(action)

                self._changes[name] = True

                self.logger.debug('action %s added to db' % name)

    def methodChanged(self, name):
        if name in self._changes:
            return True
        return False

    @property
    def isChanged(self):
        for v in self._changes.values():
            if v is True:
                return True
        return False

    # def __repr__(self):
    #     out = ""
    #     for item in self.methodslist:
    #         out += "%s\n" % item
    #     return out

    # __str__ = __repr__
