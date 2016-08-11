from JumpScale import j

from .ModelBase import ModelBase


class ActorModel(ModelBase):
    """
    is state object for actor, what was last state after installing
    """

    def __init__(self, category, db, key=""):
        self._capnp = j.atyourservice.db.AYSModel.Actor
        ModelBase.__init__(self, category, db, key)

    @property
    def methods(self):
        methods = {}
        for action_code in self.db.actionsTemplate:
            methods[action_code.name] = action_code.actionCodeKey
        return methods

    @property
    def methodslist(self):
        """
        sorted methods
        """
        if self._methodsList == []:
            keys = sorted([item for item in self.methods.keys()])
            for key in keys:
                self._methodsList.append(self.methods[key])
        return self._methodsList

#### recurringTemplate
    @property
    def recurringTemplate(self):
        return self.dbobj.recurringTemplate

    def recurring_template_new(self, *kwargs):
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

    def actions_services_template_new(self, **kwargs):
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

    def actions_actor_new(self, **kwargs):
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

    def producer_new(self, **kwargs):
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
            if not self.dbobj['action_code'].exists(guid):
                # create new actionCode model
                action_code = j.atyourservice.AYSModel.ActionCode.new_message()
                action_code.guid = guid
                action_code.name = name
                action_code.actorName = self.actor.name
                action_code.code = source
                action_code.lastModDate = j.data.time.epoch

                # put pointer to actionCode to actor model
                action = self._actions_templates.add()
                action.name = name
                action.actionCodeKey = guid

                # save into db
                self.dbobj['action_code'].set(guid, action_code.to_bytes())
                self._changes[name] = True
                self.changed = True
                self.logger.debug('action %s added to db' % name)

    def methodChanged(self, name):
        if name in self._changes:
            return True
        return False

    # def __repr__(self):
    #     out = ""
    #     for item in self.methodslist:
    #         out += "%s\n" % item
    #     return out

    # __str__ = __repr__
