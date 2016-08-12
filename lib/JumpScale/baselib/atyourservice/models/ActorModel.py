from JumpScale import j

from JumpScale.baselib.atyourservice.models.ModelBase import ModelBase


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

#### recurringTemplate
    @property
    def recurringTemplate(self):
        return self.dbobj.recurringTemplate

    def recurringTemplateNew(self, *kwargs):
        olditems = [item.to_dict() for item in self.dbobj.recurringTemplate]
        newlist = self.dbobj.init("recurringTemplate", len(olditems) + 1)
        for i, item in enumerate(olditems):
            newlist[i] = item
        recurringTemplate = newlist[-1]
        for k, v in kwargs.items():
            if hasattr(recurringTemplate, k):
                setattr(recurringTemplate, k, v)
        return recurringTemplate

#### actionServiceTemplates
    @property
    def actionsServicesTemplate(self):
        return self.dbobj.actionsServicesTemplate

    def actionsServicesTemplateNew(self, **kwargs):
        olditems = [item.to_dict() for item in self.dbobj.actionsServicesTemplate]
        newlist = self.dbobj.init("actionsServicesTemplate", len(olditems) + 1)
        for i, item in enumerate(olditems):
            newlist[i] = item
        actionsServicesTemplate = newlist[-1]

        for k, v in kwargs.items():
            if hasattr(actionsServicesTemplate, k):
                setattr(actionsServicesTemplate, k, v)
        return actionsServicesTemplate

#### actionsActor
    @property
    def actionsActor(self):
        return self.dbobj.actionsActor

    def actionsActorNew(self, **kwargs):
        olditems = [item.to_dict() for item in self.dbobj.actionsActor]
        newlist = self.dbobj.init("actionsActor", len(olditems) + 1)
        for i, item in enumerate(olditems):
            newlist[i] = item
        actionsActor = newlist[-1]
        for k, v in kwargs.items():
            if hasattr(actionsActor, k):
                setattr(actionsActor, k, v)

#### producers
    @property
    def producers(self):
        return self.dbobj.producers

    def producerNew(self, **kwargs):
        olditems = [item.to_dict() for item in self.dbobj.producers]
        newlist = self.dbobj.init("producers", len(olditems) + 1)
        for i, item in enumerate(olditems):
            newlist[i] = item
        producer = newlist[-1]

        for k, v in kwargs.items():
            if hasattr(producer, k):
                setattr(producer, k, v)

        return producer

#### model methods
    def _post_init(self):
        # self.db.parent = j.atyourservice.AYSModel.actor.actorPointer.new_message()  # TODO
        self.dbobj.key = j.data.idgenerator.generateGUID()
        self.dbobj.ownerKey = j.data.idgenerator.generateGUID()
        self.dbobj.name = self.actor.name

    def _pre_save(self):
        pass

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
                action = self.actionsServicesTemplateNew()
                action.name = name
                action.actionCodeKey = guid

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
