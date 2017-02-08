from JumpScale import j
from JumpScale.baselib.atyourservice81.lib.models.ActorServiceBaseModel import ActorServiceBaseModel
from JumpScale.baselib.atyourservice81.lib.Service import Service
from JumpScale.baselib.atyourservice81.lib import model_capnp as ModelCapnp

VALID_STATES = ['new', 'installing', 'ok', 'error', 'disabled', 'changed']


class ServiceModel(ActorServiceBaseModel):

    def __init__(self, aysrepo, capnp_schema, category, db, index, key="", new=False):
        super().__init__(aysrepo=aysrepo, capnp_schema=capnp_schema, category=category, db=db, index=index, key=key, new=new)
        self._aysrepo = aysrepo
        self._cache = False
        self._producers = []
        self._consumers = []

    def enable_cache(self):
        self._cache = True

    def disable_cache(self):
        self._cache = False
        self._producers = []
        self._consumers = []

    @property
    def role(self):
        return self.dbobj.actorName.split(".")[0]

    @property
    def parent(self):
        if self.dbobj.parent.serviceName == '' or self.dbobj.parent.actorName == '':
            return None

        parents = self._aysrepo.servicesFind(name=self.dbobj.parent.serviceName, actor=self.dbobj.parent.actorName)
        # parentModels = self._aysrepo.db.services.find(
        #     name=self.dbobj.parent.serviceName, actor=self.dbobj.parent.actorName)
        if len(parents) <= 0:
            return None
        elif len(parents) > 1:
            raise j.exceptions.RuntimeError("More then one parent model found for model %s:%s" %
                                            (self.dbobj.actorName, self.dbobj.name))

        return parents[0].model

    def _executeActionService(self, action, args={}):
        # execute an action in process without creating a job
        # usefull for methods called very often.
        action_id = self.actions[action].actionKey
        action_model = j.core.jobcontroller.db.actions.get(action_id)
        action_with_lines = ("\n%s \n" % action_model.code)
        indented_action = '\n    '.join(action_with_lines.splitlines())
        complete_action = "def %s(%s): %s" % (action, action_model.argsText, indented_action)
        exec(complete_action)
        res = eval(action)(service=self, args=args)
        return res

    def _build_actions_chain(self, action, ds=list(), parents=list(), dc=None):
        """
        this method returns a list of action that need to happens before the action passed in argument
        can start
        """
        if dc is None:
            dependency_chain = self._executeActionService('init_actions_', args={'action': action})
        if action in parents:
            raise RuntimeError('cyclic dep: %s' % parents)
        if action in ds:
            return
        ds.append(action)
        newkeys = dependency_chain.get(action)
        if not newkeys:
            return
        parents.append(action)
        for key in newkeys:
            self._build_actions_chain(key, ds, parents, dc)
        parents.pop()
        return

    @property
    def producers(self):
        # producers = None
        # if self._cache is True:
        #     if self._producers != []:
        #         return self._producers
        #     else:
        #         producers = self._producers
        # else:
        #     producers = []
        producers = []

        for prod in self.dbobj.producers:
            producers.extend(self._aysrepo.servicesFind(name=prod.serviceName, actor=prod.actorName))
            # producers.extend(self._aysrepo.db.services.find(name=prod.serviceName, actor=prod.actorName))
        return [p.model for p in producers]

    def getProducersRecursive(self, producers=set(), action="", producerRoles="*"):
        for producer_model in self.producers:
            if action == "" or action in producer_model.actions.keys():
                if producerRoles == "*" or producer_model.role in producerRoles:
                    producers.add(producer_model)
            producers = producer_model.getProducersRecursive(
                producers=producers, action=action, producerRoles=producerRoles)
        return producers

    @property
    def consumers(self):
        consumers = None
        if self._cache is True:
            if self._consumers != []:
                return self._consumers
            else:
                consumers = self._consumers
        else:
            consumers = []

        for cons in self.dbobj.consumers:
            consumers.extend(self._aysrepo.servicesFind(name=cons.serviceName, actor=cons.actorName))
            # producers.extend(self._aysrepo.db.services.find(name=prod.serviceName, actor=prod.actorName))
        return [c.model for c in consumers]


    def getConsumersRecursive(self, consumers=set(), action="", consumersRoles="*"):
        for consumer_model in self.consumers:
            if action == "" or action in consumer_model.actions.keys():
                if consumersRoles == "*" or consumer_model.role in consumersRoles:
                    consumers.add(consumer_model)
            consumers = consumer_model.getProducersRecursive(
                consumers=consumers, action=action, consumersRoles=producerRoles)
        return consumers

    def index(self):
        # put indexes in db as specified
        if self.dbobj.parent.actorName != "":
            parent = "%s!%s" % (self.dbobj.parent.actorName, self.dbobj.parent.serviceName)
        else:
            parent = ""

        if len(self.dbobj.producers) == 0:
            ind = "%s:%s:%s:%s:%s" % (self.dbobj.name, self.dbobj.actorName, self.dbobj.state, parent, "")
            self._index.index({ind: self.key})
        else:
            # now batch all producers as more than 1 index
            #@TODO: *1 test
            index = {}
            for producer in self.dbobj.producers:
                producer2 = "%s!%s" % (producer.actorName, producer.serviceName)
                ind = "%s:%s:%s:%s:%s" % (self.dbobj.name, self.dbobj.actorName, self.dbobj.state, parent, producer2)
                index[ind] = self.key
            self._index.index(index)

    def delete(self):
        # delete indexes from db
        if self.dbobj.parent.actorName != "":
            parent = "%s!%s" % (self.dbobj.parent.actorName, self.dbobj.parent.serviceName)
        else:
            parent = ""

        if len(self.dbobj.producers) == 0:
            key = "%s:%s:%s:%s:%s" % (self.dbobj.name, self.dbobj.actorName, self.dbobj.state, parent, "")
            self._index.index_remove(key)
        else:
            # now batch all producers as more than 1 index
            for producer in self.dbobj.producers:
                producer2 = "%s!%s" % (producer.actorName, producer.serviceName)
                key = "%s:%s:%s:%s:%s" % (self.dbobj.name, self.dbobj.actorName, self.dbobj.state, parent, producer2)
                self._index.index_remove(key)

        # delete actual model object
        if self._db.exists(self.key):
            self._db.delete(self.key)

    def objectGet(self, aysrepo):
        """
        returns an Service object created from this model
        """
        if self.key not in self._aysrepo._services:
            self._aysrepo._services[self.key] = Service.init_from_model(aysrepo=aysrepo, model=self)
        return self._aysrepo._services[self.key]
        # service = Service(name=self.dbobj.name, aysrepo=aysrepo, model=self)
        # return service

    @property
    def wiki(self):
        # TODO: *3
        raise NotImplemented
        out = "## service:%s state" % self.service.key

        if self.parent != "":
            out += "\n- parent:%s\n\n" % self.parent

        if self.producers != {}:
            out = "### producers\n\n"
            out += "| %-20s | %-30s |\n" % ("role", "producer")
            out += "| %-20s | %-30s |\n" % ("---", "---")
            for role, producers in self.producers.items():
                for producer in producers:
                    out += "| %-20s | %-30s |\n" % (role, producer)
            out += "\n"

        if self.recurring != {} or self.methods != {}:
            methods = OrderedDict()
            for actionname, actionstate in self.methods.items():
                methods[actionname] = [actionstate, "", 0]
            for actionname, obj in self.recurring.items():
                period, last = obj
                actionstate, _, _ = methods[actionname]
                methods[actionname] = [actionstate, period, int(last)]

            out = "### actions\n\n"
            out += "| %-20s | %-10s | %-10s | %-30s |\n" % (
                "name", "state", "period", "last")
            out += "| %-20s | %-10s | %-10s | %-30s |\n" % (
                "---", "---", "---", "---")
            for actionname, obj in methods.items():
                actionstate, period, last = obj
                out += "| %-20s | %-10s | %-10s | %-30s |\n" % (
                    actionname, actionstate, period, last)
            out += "\n"

        return out

    def actionCheckExecuted(self, action):
        """
        check if it needs to be executed or not
        """
        from IPython import embed
        print("DEBUG NOW actionCheckExecuted")
        embed()
        raise RuntimeError("stop debug here")

    def producerAdd(self, actorName, serviceName, key):
        """
        Add another service to the producers list
        """
        obj = j.data.capnp.getMemoryObj(
            schema=self._capnp_schema.ServicePointer,
            actorName=actorName,
            serviceName=serviceName,
            key=key)

        self.dbobj.producers.append(obj)
        self.save()

    def producerRemove(self, service):
        """
        Remove the service passed in argument from the producers list
        """
        for i, prod in enumerate(self.dbobj.producers):
            if prod.key == service.model.key:
                self.dbobj.producers.pop(i)

    def consumerAdd(self, actorName, serviceName, key):
        """
        Add another service to the consumers list
        """
        obj = j.data.capnp.getMemoryObj(
            schema=self._capnp_schema.ServicePointer,
            actorName=actorName,
            serviceName=serviceName,
            key=key)

        self.dbobj.consumers.append(obj)
        self.save()

    def consumerRemove(self, service):
        """
        Remove the service passed in argument from the producers list
        """
        for i, consumer in enumerate(self.dbobj.consumers):
            if consumer.key == service.model.key:
                self.dbobj.consumers.pop(i)

# events

    def eventFilterSet(self, command, actions, channel="", tags="", secrets=""):
        self.logger.debug('set event filter on %s!%s' % (self.role, self.name))
        changed = False

        command = command.lower()
        channel = channel.lower()
        # action = actions.lower()
        tags = tags.lower()
        tags = self._getSortedListInString(tags)

        res = self.eventFiltersFind(command=command, channel=channel, actions=actions, tags=tags)
        if len(res) == 0:
            eventsFilter = j.data.capnp.getMemoryObj(ModelCapnp.EventFilter)
            self.dbobj.eventFilters.append(eventsFilter)
        elif len(res) == 1:
            eventsFilter = res[0]
        else:
            raise j.exceptions.Input(message="found more than 1 eventsfilter", level=1, source="", tags="", msgpub="")

        if command != '':
            eventsFilter.command = command
            changed = True
        if channel != "":
            eventsFilter.channel = channel
            changed = True

        if j.data.types.string.check(actions):
            actions = actions.split(',')

        if not j.data.types.list.check(actions):
            raise j.exceptions.Input('actions for eventFilter should be a list')

        for action in actions:
            eventsFilter.actions.append(action.lower())
        if len(actions) > 0:
            changed = True

        if tags != "":
            eventsFilter.tags = tags
            changed = True
        if secrets != "":
            secrets = self._getSortedListInString(secrets)
            eventsFilter.secrets = secrets
            changed = True

        self.changed = changed

        return changed

    def _getSortedListInString(self, items):
        # sort & structure tags well
        items = [item.strip().strip(",").strip() for item in items.split(" ") if item.strip() != ""]
        items.sort()
        items = " ".join(items)
        return items

    def eventFiltersFind(self, command='', channel="", actions=[], tags=""):
        command = command.lower()
        channel = channel.lower()
        actions = [action.lower() for action in actions]
        tags = tags.lower()
        tags = self._getSortedListInString(tags)

        res = []
        for item in self.dbobj.eventFilters:
            found = True
            if command != '' and item.command != command:
                found = False
            if channel != "" and item.channel != channel:
                found = False
            if found and tags != "" and len(item.tags) > 5 and tags.find(item.tags) == -1:
                found = False
            for action in actions:
                if found and action != "" and action not in item.actions:
                    found = False
            if found:
                res.append(item)
        return res
# others

    @property
    def dictFiltered(self):
        ddict = super().dictFiltered
        # ddict = self.dbobj.to_dict()
        if "data" in ddict:
            ddict.pop("data")
        return ddict

    def _pre_save(self):
        binary = self.data.to_bytes_packed()
        self._data = None
        if binary != b'':
            self.dbobj.data = binary

    def __repr__(self):
        # TODO: *1 to put back on self.wiki
        # out = self.dictJson + "\n"
        # if self.dbobj.dataSchema not in ["", b""]:
        #     out += "SCHEMA:\n"
        #     out += self.dbobj.dataSchema
        # if self.dbobj.data not in ["", b""]:
        #     out += "DATA:\n"
        #     out += self.dataJSON
        # return out
        return "%s!%s" % (self.role, self.dbobj.name)

    def __eq__(self, other):
        if not isinstance(other, ServiceModel):
            return False
        return self.key == other.key

    def __hash__(self):
        return hash(self.key)

    __str__ = __repr__
