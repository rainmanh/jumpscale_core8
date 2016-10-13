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
        self.name = name
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

        r = self.model._gitRepoNowObj()
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
        skey = "%s!%s" % (self.model.role, self.model.dbobj.name)
        parent = self._initParent(actor, args)
        if parent is not None:
            fullpath = j.sal.fs.joinPaths(parent.path, skey)
            r.path = j.sal.fs.pathRemoveDirPart(fullpath, self.aysrepo.path)
        else:
            r.path = j.sal.fs.joinPaths("services", skey)

        self._initProducers(actor, args)
        self._initRecurringActions(actor)
        self._initEventActions(actor)

        # set default value for argument not specified in blueprint
        template = self.aysrepo.templateGet(actor.model.name)
        for k, v in template.schemaHrd.items.items():
            if k not in args:
                args[k] = v.default

        # input will always happen in process
        args2 = self.input(args=args)
        if args2 != args:
            args.update(args2)
        if not j.data.types.dict.check(args):
            raise j.exceptions.Input(message="result from input needs to be dict,service:%s" % self,
                                     level=1, source="", tags="", msgpub="")

        dbobj.data = j.data.capnp.getBinaryData(j.data.capnp.getObj(dbobj.dataSchema, args=args))

        self.init()

        self.model.save()

        self.saveToFS()

    def _initParent(self, actor, args):
        if actor.model.dbobj.parent.actorRole is not "":
            parent_role = actor.model.dbobj.parent.actorRole

            # try to get the instance name from the args. Look for full actor name ('node.ssh') or just role (node)
            # if none of the two is available in the args, don't use instance name and expect the parent service to be unique in the repo
            parent_name = args.get(parent_role, '')
            res = self.aysrepo.servicesFind(name=parent_name, actor='%s.*' % parent_role)
            res = [s for s in res if s.model.role == parent_role]
            if len(res) == 0:
                if actor.model.dbobj.parent.auto is False:
                    raise j.exceptions.Input(message="could not find parent:%s for %s, found 0" %
                                             (parent_name, self), level=1, source="", tags="", msgpub="")
                else:
                    auto_actor = self.aysrepo.actorGet(parent_role)
                    instance = j.data.idgenerator.generateIncrID('parent_%s' % parent_role)
                    res.append(auto_actor.serviceCreate(instance="auto_%d" % instance, args={}))
            elif len(res) > 1:
                raise j.exceptions.Input(message="could not find parent:%s for %s, found more than 1." %
                                         (parent_name, self), level=1, source="", tags="", msgpub="")
            parentobj = res[0]
            self._parent = parentobj

            self.model.dbobj.parent.actorName = parentobj.model.dbobj.actorName
            self.model.dbobj.parent.key = parentobj.model.key
            self.model.dbobj.parent.serviceName = parentobj.name

            return parentobj

        return None

    def _initProducers(self, actor, args):
        if self._producers is None:
            self._producers = []

        for i, producer_model in enumerate(actor.model.dbobj.producers):
            producer_role = producer_model.actorRole

            instances = args.get(producer_role, "")

            if not j.data.types.list.check(instances):
                instances = [instances]

            for i in instances:
                res = self.aysrepo.servicesFind(name=i, actor='%s.*' % producer_role)
                res = [s for s in res if s.model.role == producer_role]

                if len(res) == 0:
                    if producer_model.auto is False:
                        raise j.exceptions.Input(message="could not find producer:%s for %s, found 0" %
                                                 (producer_role, self), level=1, source="", tags="", msgpub="")
                    else:
                        auto_actor = self.aysrepo.actorGet(producer_role)
                        instance = j.data.idgenerator.generateIncrID('service_%s' % producer_role)
                        res.append(auto_actor.serviceCreate(instance="auto_%d" % instance, args={}))
                elif len(res) > 1:
                    raise j.exceptions.Input(message="could not find producer:%s for %s, found more than 1." %
                                             (producer_role, self), level=1, source="", tags="", msgpub="")

                producer_obj = res[0]
                self.model.producerAdd(
                    actorName=producer_obj.model.dbobj.actorName,
                    serviceName=producer_obj.model.dbobj.name,
                    key=producer_obj.model.key)

        # add the parent to the producers
        if self.parent is not None:
            producer = self.model.producerAdd(
                actorName=self.parent.model.dbobj.actorName,
                serviceName=self.parent.model.dbobj.name,
                key=self.parent.model.key)

    def _initRecurringActions(self, actor):
        self.model.dbobj.init('recurringActions', len(actor.model.dbobj.recurringActions))

        for i, reccuring_info in enumerate(actor.model.dbobj.recurringActions):
            recurring = self.model.dbobj.recurringActions[i]
            recurring.action = reccuring_info.action
            recurring.period = reccuring_info.period
            recurring.log = reccuring_info.log
            recurring.lastRun = 0

    def _initEventActions(self, actor):
        self.model.dbobj.init('eventActions', len(actor.model.dbobj.eventActions))

        for i, event_info in enumerate(actor.model.dbobj.eventActions):
            event = self.model.dbobj.eventActions[i]
            event.action = event_info.action
            event.event = event_info.event
            event.log = event_info.log
            event.lastRun = 0

    def _check_args(self, actor, args):
        """ Checks whether if args are the same as in instance model """
        data = j.data.serializer.json.loads(self.model.dataJSON)
        for key, value in args.items():
            sanitized_key = j.data.hrd.sanitize_key(key)
            if data[sanitized_key] != value:
                self.processChange(actor=actor, changeCategory="dataschema", args=args)
                break

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

    def reload(self):
        self.model._data = None
        self.model.load(self.model.key)

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

    def delete(self):
        """
        delete this service completly.
        remove it from db and from filesystem
        all the children of this service are going to be deleted too
        """
        for service in self.children:
            service.delete()

        self.model.delete()
        j.sal.fs.removeDirTree(self.path)
        self.aysrepo._services.remove(self)

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
                    self._producers[prod_model.role] = []

                result = self.aysrepo.servicesFind(name=prod_model.dbobj.name, actor=prod_model.dbobj.actorName)
                for service in result:
                    self._producers[prod_model.role].append(service)

        return self._producers

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
        for service in target.consumers:
            out.add(service)
            self.findConsumersRecursive(service, out)
        return out

    def getProducersRecursive(self, producers=set(), callers=set(), action="", producerRoles="*"):
        for role, producers_list in self.producers.items():
            for producer in producers_list:
                if action == "" or action in producer.model.actionsState.keys():
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

            if producer.model.actionsState['init'] != "ok":
                producersChanged.add(producer)

            if producer.model.actionsState['install'] != "ok":
                producersChanged.add(producer)

            if action not in producer.model.actionsState.keys():
                continue

            if producer.model.actionsState[action] != "ok":
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
            serviceName=service.name,
            key=service.model.key)

        if service.model.dbobj.actorName not in self._producers:
            self._producers[service.model.dbobj.actorName] = [service]
        else:
            self._producers[service.model.dbobj.actorName].append(service)

        self.saveAll()

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
            if 'getExecutor' in service.model.actionsState.keys():
                job = service.getJob('getExecutor')
                executor = job.method(job)
                return executor
        return j.tools.executor.getLocal()

    def processChange(self, actor, changeCategory, args={}):
        """
        template action change
        categories :
            - dataschema
            - ui
            - config
            - action_new_actionname
            - action_mod_actionname
        """
        # TODO: implement different pre-define action for each category
        # self.logger.debug('process change for %s (%s)' % (self, changeCategory)

        if changeCategory == 'dataschema':
            # We use the args passed without change
            pass

        elif changeCategory == 'ui':
            # TODO
            pass
        elif changeCategory == 'config':
            # update the recurrin and event actions
            # then set the lastrun to the value it was before update
            recurring_lastrun = {}
            event_lastrun = {}

            for event in self.model.actionsEvent.values():
                event_lastrun[event.action] = event.lastRun
            for recurring in self.model.actionsRecurring.values():
                recurring_lastrun[recurring.action] = recurring.lastRun

            self._initRecurringActions(actor)
            self._initEventActions(actor)

            for action, lastRun in event_lastrun.items():
                self.model.actionsEvent[action].lastRun = lastRun
            for action, lastRun in recurring_lastrun.items():
                self.model.actionsRecurring[action].lastRun = lastRun

        elif changeCategory.find('action_new') != -1:
            action_name = changeCategory.split('action_new_')[1]
            actor_action_pointer = actor.model.actions[action_name]
            self.model.actionAdd(actor_action_pointer.actionKey, action_name)

        elif changeCategory.find('action_mod') != -1:
            # update state and pointer of the action pointer in service model
            action_name = changeCategory.split('action_mod_')[1]
            action_actor_pointer = actor.model.actions[action_name]
            service_action_pointer = self.model.actions[action_name]
            service_action_pointer.state = 'changed'
            service_action_pointer.actionKey = action_actor_pointer.actionKey

            # update the lastModDate of the action object
            action = j.core.jobcontroller.db.action.get(key=service_action_pointer.actionKey)
            action.dbobj.lastModDate = j.data.time.epoch
            action.save()

        # execute the processChange method if it exists
        if 'processChange' in self.model.actions.keys():
            args.update({'changeCategory': changeCategory})
            job = self.getJob("processChange", args=args)
            args = job.executeInProcess(service=self)
            job.model.save()
            # self.runAction('processChange', args={'changeCategory': changeCategory})

        self.model.save()

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
        self.logger.debug('start runAction %s on %s' % (action, self))
        job = self.getJob(actionName=action, args=args)
        now = j.data.time.epoch
        p = job.execute()

        while not p.isDone():
            p.wait()

        # if the action is a reccuring action, save last execution time in model
        if action in self.model.actionsRecurring:
            self.model.actionsRecurring[action].lastRun = now

        service_action_obj = self.model.actions[action]

        if p.state != 'success':
            job.model.dbobj.state = 'error'
            service_action_obj.state = 'error'
            # processError creates the logs entry in job object
            job._processError(p.error)
        else:
            job.model.dbobj.state = 'ok'
            service_action_obj.state = 'ok'

            log_enable = j.core.jobcontroller.db.action.get(service_action_obj.actionKey).dbobj.log
            if log_enable:
                job.model.log(msg=p.stdout, level=5, category='out')
                job.model.log(msg=p.stderr, level=5, category='err')

            if p.stdout != '':
                print(p.stdout)

        job.model.save()
        job.service.saveAll()
        self.logger.debug('end runAction %s on %s' % (action, self))
        return job

    def getJob(self, actionName, args={}):
        action = self.model.actions[actionName]
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

    def __eq__(self, service):
        if not service:
            return False
        return service.model.key == self.model.key

    def __hash__(self):
        return hash(self.model.key)

    def __repr__(self):
        return "service:%s!%s" % (self.model.role, self.model.dbobj.name)

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
