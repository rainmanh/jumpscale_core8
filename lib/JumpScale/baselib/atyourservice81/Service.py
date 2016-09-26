from JumpScale import j

import capnp


class Service:

    def __init__(self, aysrepo, actor=None, model=None, name="", args={}):
        """
        init from a template or from a model
        """
        self._schema = None
        self._path = ""
        self._schema = None
        self._producers = {}
        self._name = name
        self._parent = None
        self._executor = None

        self.aysrepo = aysrepo
        self.logger = j.atyourservice.logger
        self.db = aysrepo.db.service

        if actor is not None:
            self._initFromActor(actor, args=args, name=name)
        elif model is not None:
            self.model = model
        else:
            raise j.exceptions.Input(
                message="template or model needs to be specified when creating an actor", level=1, source="", tags="", msgpub="")

    @property
    def path(self):
        if self._path == "":
            relpath = self.model.dbobj.gitRepos[0].path
            assert self.model.dbobj.gitRepos[0].url == self.aysrepo.git.remoteUrl
            self._path = j.sal.fs.joinPaths(self.aysrepo.path, relpath)
        return self._path

    def _initFromActor(self, actor, name, args={}):

        if j.data.types.string.check(actor):
            raise j.exceptions.RuntimeError("no longer supported, pass actor")

        if actor is None:
            raise j.exceptions.RuntimeError("service actor cannot be None")

        self.model = self.aysrepo.db.service.new()
        dbobj = self.model.dbobj
        dbobj.name = name
        dbobj.actorName = actor.model.dbobj.name
        dbobj.actorKey = actor.model.key
        dbobj.state = "new"
        dbobj.dataSchema = actor.model.dbobj.serviceDataSchema

        r = self.model.gitRepoAdd()
        r.url = self.aysrepo.git.remoteUrl

        # actions
        actions = dbobj.init("actions", len(actor.model.dbobj.actions))
        counter = 0
        for action in actor.model.dbobj.actions:
            actionnew = actions[counter]
            actionnew.state = "new"
            actionnew.actionKey = action.actionKey
            actionnew.name = action.name
            counter += 1

        # parents/producers
        skey = "%s!%s" % (self.model.role, self.model.name)
        parent = self._initParent(actor, args)
        if parent is not None:
            fullpath = j.sal.fs.joinPaths(parent.path, skey)
            r.path = j.sal.fs.pathRemoveDirPart(fullpath, self.aysrepo.path)
        else:
            r.path = j.sal.fs.joinPaths("services", skey)

        self._initProducers(actor, args)

        # input will always happen in process
        args = self.input(args=args)
        if not j.data.types.dict.check(args):
            raise j.exceptions.Input(message="result from input needs to be dict,service:%s" % self,
                                     level=1, source="", tags="", msgpub="")

        dbobj.data = j.data.capnp.getBinaryData(j.data.capnp.getObj(dbobj.dataSchema, args=args))

        self.init()

        self.model.save()

        self.saveToFS()

        # TODO *1*
        # # Set subscribed event into state
        # if self.actor.template.hrd is not None:
        #     for event, actions in self.actor.template.hrd.getDictFromPrefix('events').items():
        #         self.model.setEvents(event, actions)
        #     # Set recurring into state
        #     for action, period in self.actor.template.hrd.getDictFromPrefix('recurring').items():
        #         self.model.setRecurring(action, period)
        #
        #     # if service.hrd has remove some event action, update state to
        #     # reflect that
        #     actual = set(self.actor.template.hrd.getDictFromPrefix('events').keys())
        #     total = set(self.model.events.keys())
        #     for action in total.difference(actual):
        #         self.model.removeEvent(action)
        #
        #     # if service.hrd has remove some recurring action, update state to
        #     # reflect that
        #     actual = set(self.actor.template.hrd.getDictFromPrefix('recurring').keys())
        #     total = set(self.model.recurring.keys())
        #     for action in total.difference(actual):
        #         self.model.removeRecurring(action)
        #
        # self.model.save()

    def _initParent(self, actor, args):
        if actor.model.dbobj.parent.actorRole is not "":
            parent_role = actor.model.dbobj.parent.actorRole

            # try to get the instance name from the args. Look for full actor name ('node.ssh') or just role (node)
            # if none of the two is available in the args, don't use instance name and expect the parent service to be unique in the repo
            parent_name = args.get(parent_role, None)
            res = self.aysrepo.servicesFind(name=parent_name, actor='%s.*' % parent_role)
            if len(res) == 0:
                raise j.exceptions.Input(message="could not find parent:%s for %s, found 0" %
                                         (actor_name, self), level=1, source="", tags="", msgpub="")
            elif len(res) > 1:
                raise j.exceptions.Input(message="could not find parent:%s for %s, found more than 1." %
                                         (actor_name, self), level=1, source="", tags="", msgpub="")
            parentobj = res[0]
            self._parent = parentobj

            self.model.dbobj.parent.actorName = parentobj.model.dbobj.actorName
            self.model.dbobj.parent.key = parentobj.model.key
            self.model.dbobj.parent.serviceName = parent_name

            return parentobj

        return None

    def _initProducers(self, actor, args):
        if self._producers is None:
            self._producers = []

        producers_size = len(actor.model.dbobj.producers)
        # the parent is also considered an producers
        # we need this to be able to build the dependency tree
        if self.parent is not None:
            producers_size += 1

        self.model.dbobj.init('producers', producers_size)
        for i, producer_model in enumerate(actor.model.dbobj.producers):
            producer_role = producer_model.actorRole

            instance = args.get(producer_role, "")
            res = self.aysrepo.servicesFind(name=instance, actor='%s.*' % producer_role)
            if len(res) == 0:
                if producer_model.auto is False:
                    raise j.exceptions.Input(message="could not find producer:%s for %s, found 0" %
                                             (producer_role, self), level=1, source="", tags="", msgpub="")
                else:
                    auto_actor = self.aysrepo.actorGet(producer_role)
                    # TODO: generate incremental instance name
                    res.append(auto_actor.serviceCreate(instance="auto", args=args))
            elif len(res) > 1:
                raise j.exceptions.Input(message="could not find producer:%s for %s, found more than 1." %
                                         (producer_role, self), level=1, source="", tags="", msgpub="")

            producer = self.model.dbobj.producers[i]
            producer_obj = res[0]

            producer.actorName = producer_obj.model.dbobj.actorName
            producer.key = producer_obj.model.key
            producer.serviceName = producer_obj.model.name

        # add the parent to the producers
        if self.parent is not None:
            producer = self.model.dbobj.producers[producers_size - 1]
            producer.actorName = self.parent.model.dbobj.actorName
            producer.key = self.parent.model.key
            producer.serviceName = self.parent.model.name

    def loadFromFS(self):
        """
        get content from fs and load in object
        only for DR purposes, std from key value stor
        """
        # TODO: *2 implement
        from IPython import embed
        print("DEBUG NOW loadFromFS")
        embed()
        raise RuntimeError("stop debug here")

        self.model.save()

    def saveToFS(self):
        j.sal.fs.createDir(self.path)
        path2 = j.sal.fs.joinPaths(self.path, "service.json")
        j.sal.fs.writeFile(path2, self.model.dictJson, append=False)

        path3 = j.sal.fs.joinPaths(self.path, "data.json")
        j.sal.fs.writeFile(path3, self.model.dataJSON)

        path4 = j.sal.fs.joinPaths(self.path, "schema.capnp")
        j.sal.fs.writeFile(path4, self.model.dbobj.dataSchema)

    def save(self):
        self.model.save()

    def saveAll(self):
        self.model.save()
        self.saveToFS()

    def reset(self):
        self._hrd = None
        # self._yaml = None
        self._mongoModel = None
        self._dnsNames = []
        self._logPath = None
        self._state = None
        self._executor = None
        self._producers = None
        self._parentChain = None
        self._parent = None
        self._path = ""
        self._schema = ""

    @property
    def parent(self):
        if self._parent is None:
            if self.model.parent is not None:
                self._parent = self.model.parent.objectGet(self.aysrepo)
        return self._parent

    @property
    def parents(self):
        chain = []
        parent = self.parent
        while parent is not None:
            chain.append(parent)
            parent = parent.parent
        return chain

    @property
    def children(self):
        res = []
        for service in self.aysrepo.services:
            if service.parent == self:
                res.append(service)
        return res

    @property
    def producers(self):
        if self._producers == {}:
            for prod_model in self.model.producers:

                if prod_model.dbobj.actorName not in self._producers:
                    self._producers[prod_model.dbobj.actorName] = []

                result = self.aysrepo.servicesFind(name=prod_model.dbobj.name, actor=prod_model.dbobj.actorName)
                for service in result:
                    self._producers[prod_model.dbobj.actorName].append(service)

        return self._producers

    def findProducer(self, role, name):
        if role in self.producers:
            for producer in self.producers[role]:
                if producer.model.name in name:
                    return producer
        return None

    @property
    def consumers(self):
        consumers = list()
        services = self.aysrepo.servicesFind()
        for service in services:
            if self.isConsumedBy(service):
                consumers.append(service)
        return consumers

    def isConsumedBy(self, service):
        if self.model.role in service.producers:
            for s in service.producers[self.model.role]:
                if s.model.key == self.model.key:
                    return True
        return False

    def findConsumersRecursive(self, target=None, out=set()):
        """
        @return set of services that consumes target, recursivlely
        """
        if target is None:
            target = self
        for service in self.findConsumers(target):
            out.add(service)
            self.findConsumersRecursive(service, out)
        return out

    def getProducersRecursive(self, producers=set(), callers=set(), action="", producerRoles="*"):
        for role, producers_list in self.producers.items():
            for producer in producers_list:
                if action == "" or action in producer.model.methodsState.keys():
                    if producerRoles == "*" or producer.model.role in producerRoles:
                        producers.add(producer)
                producers = producer.getProducersRecursive(
                    producers=producers, callers=callers, action=action, producerRoles=producerRoles)
        return producers.symmetric_difference(callers)

    def printProducersRecursive(self, prefix=""):
        for role, producers2 in self.producers.items():
            # print ("%s%s"%(prefix,role))
            for producer in producers2:
                print("%s- %s" % (prefix, producer))
                producer.printProducersRecursive(prefix + "  ")

    def getProducersWaiting(self, action="install", producersChanged=set(), scope=None):
        """
        return list of producers which are waiting to be executing the action
        """

        for producer in self.getProducersRecursive(set(), set()):
            # check that the action exists, no need to wait for other actions,
            # appart from when init or install not done

            if producer.model.methodsState['init'] != "ok":
                producersChanged.add(producer)

            if producer.model.methodsState['install'] != "ok":
                producersChanged.add(producer)

            if action not in producer.model.methodsState.keys():
                continue

            if producer.model.methodsState[action] != "ok":
                producersChanged.add(producer)

        if scope is not None:
            producersChanged = producersChanged.intersection(scope)

        return producersChanged

    def consume(self, service):
        """
        consume another service dynamicly
        """
        if service in self.producers:
            return

        self.model.producerAdd(
            actorName=service.model.dbobj.actorName,
            serviceName=service.model.name,
            key=service.model.key)

    @property
    def executor(self):
        if self._executor is None:
            self._executor = self._getExecutor()
        return self._executor

    def _getExecutor(self):
        executor = None
        tocheck = [self]
        tocheck.extend(self.parents)
        for service in tocheck:
            if 'getExecutor' in service.model.methodsState.keys():
                job = service.getJob('getExecutor')
                executor = job.method(job)
                return executor
        return j.tools.executor.getLocal()

    def processChange(self, item):
        # TODO
        pass

    def input(self, args={}):
        job = self.getJob("input", args=args)
        args = job.executeInProcess(service=self)
        job.model.save()
        return args

    def init(self):
        job = self.getJob(actionName="init")
        job.executeInProcess(service=self)
        job.model.save()
        return job

    def runAction(self, action, args={}):
        job = self.getJob(actionName=action, args=args)
        args = job.execute()
        job.model.save()
        return job

    def getJob(self, actionName, args={}):
        action = self.getActionObj(actionName)
        jobobj = j.core.jobcontroller.db.job.new()
        jobobj.dbobj.actionKey = action.actionKey
        jobobj.dbobj.actionName = action.name
        jobobj.dbobj.actorName = self.model.dbobj.actorName
        jobobj.dbobj.serviceName = self.model.dbobj.name
        jobobj.dbobj.serviceKey = self.model.key
        jobobj.dbobj.state = "new"
        jobobj.dbobj.lastModDate = j.data.time.epoch
        jobobj.args = args
        job = j.core.jobcontroller.newJobFromModel(jobobj)
        return job

    def getActionObj(self, actionName):
        for action in self.model.dbobj.actions:
            if action.name == actionName:
                return action
        raise j.exceptions.Input(message="Could not find action:%s in %s"(
            actionName, self), level=1, source="", tags="", msgpub="")

    def __eq__(self, service):
        if not service:
            return False
        return service.model.key == self.model.key

    def __hash__(self):
        return hash(self.model.key)

    def __repr__(self):
        return "service:%s!%s" % (self.model.role, self.model.name)

    def __str__(self):
        return self.__repr__()

    def _getDisabledProducers(self):
        disabled = []
        for producers_list in self.producers.values():
            for producer in producers_list:
                if producer.model.dbobj.state == 'disabled':
                    disabled.append(producer)
        return disabled

    # def disable(self):
    #     for consumer in self.getConsumers():
    #         candidates = self.aysrepo.findServices(role=self.model.role, first=False)
    #         if len(candidates) > 1:
    #             # Other candidates available. Should link consumer to new
    #             # candidate
    #             candidates.remove(self)
    #             candidate = candidates[0]
    #             producers = consumer.hrd.getList('producer.%s' % self.role, [])
    #             producers.remove(self.key)
    #             producers.append(candidate.key)
    #             consumer.hrd.set('producer.%s' % self.role, producers)
    #         else:
    #             # No other candidates already installed. Disable consumer as
    #             # well.
    #             consumer.disable()
    #
    #     self.log("disable instance")
    #     self.model.hrd.set('disabled', True)
    #
    # def _canBeEnabled(self):
    #     for role, producers in list(self.producers.items()):
    #         for producer in producers:
    #             if producer.state.hrd.getBool('disabled', False):
    #                 return False
    #     return True
    #
    # def enable(self):
    #     # Check that all dependencies are enabled
    #
    #     if not self._canBeEnabled():
    #         self.log(
    #             "%s cannot be enabled because one or more of its producers is disabled" % self)
    #         return
    #
    #     self.model.hrd.set('disabled', False)
    #     self.log("Enable instance")
    #     for consumer in self._getConsumers(include_disabled=True):
    #         consumer.enable()
    #         consumer.start()
    #
