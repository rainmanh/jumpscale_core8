from JumpScale import j

import capnp
import time

class Service:

    def __init__(self, aysrepo, actor=None, model=None, name="", args={}, path=None):
        """
        init from a template or from a model
        """
        self.model = None
        self._schema = None
        self._path = ""
        self._schema = None
        self.name = name

        self.aysrepo = aysrepo
        self.logger = j.atyourservice.logger

        if actor is not None:
            self._initFromActor(actor, args=args, name=name)
        elif model is not None:
            self.model = model
        elif path is not None:
            self.loadFromFS(path)
        else:
            raise j.exceptions.Input(
                message="template or model needs to be specified when creating an actor", level=1, source="", tags="", msgpub="")

    @property
    def path(self):
        if self._path == "":
            relpath = self.model.dbobj.gitRepo.path
            assert self.model.dbobj.gitRepo.url == self.aysrepo.git.remoteUrl
            self._path = j.sal.fs.joinPaths(self.aysrepo.path, relpath)
        return self._path

    def _initFromActor(self, actor, name, args={}):

        if j.data.types.string.check(actor):
            raise j.exceptions.RuntimeError("no longer supported, pass actor")

        if actor is None:
            raise j.exceptions.RuntimeError("service actor cannot be None")

        self.model = self.aysrepo.db.services.new()
        dbobj = self.model.dbobj
        dbobj.name = name
        dbobj.actorName = actor.model.dbobj.name
        dbobj.actorKey = actor.model.key
        dbobj.state = "new"
        dbobj.dataSchema = actor.model.dbobj.serviceDataSchema

        skey = "%s!%s" % (self.model.role, self.model.dbobj.name)
        dbobj.gitRepo.url = self.aysrepo.git.remoteUrl
        dbobj.gitRepo.path = j.sal.fs.joinPaths("services", skey)

        # actions
        actions = dbobj.init("actions", len(actor.model.dbobj.actions))
        counter = 0
        for action in actor.model.dbobj.actions:
            actionnew = actions[counter]
            actionnew.state = "new"
            actionnew.actionKey = action.actionKey
            actionnew.name = action.name
            actionnew.log = action.log
            actionnew.period = action.period
            counter += 1

        # set default value for argument not specified in blueprint
        template = self.aysrepo.templateGet(actor.model.name)
        for k, v in template.schemaHrd.items.items():
            if k not in args:
                args[k] = v.default

        # input will always happen in process
        args2 = self.input(args=args)
        # print("%s:%s" % (self, args2))
        if args2 is not None and j.data.types.dict.check(args2):
            args = args2

        if not j.data.types.dict.check(args):
            raise j.exceptions.Input(message="result from input needs to be dict,service:%s" % self,
                                     level=1, source="", tags="", msgpub="")

        dbobj.data = j.data.capnp.getBinaryData(j.data.capnp.getObj(dbobj.dataSchema, args=args))

        # parents/producers
        parent = self._initParent(actor, args)
        if parent is not None:
            fullpath = j.sal.fs.joinPaths(parent.path, skey)
            newpath = j.sal.fs.pathRemoveDirPart(fullpath, self.aysrepo.path)
            if j.sal.fs.exists(dbobj.gitRepo.path):
                j.sal.fs.moveDir(dbobj.gitRepo.path)
            dbobj.gitRepo.path = newpath

        self._initProducers(actor, args)

        self.save()

        self.init()

        # make sure we have the last version of the model if something changed during init
        self.reload()

        # need to do this manually cause execution of input method is a bit special.
        self.model.actions['input'].state = 'ok'

        self.saveAll()

    def _initParent(self, actor, args):
        if actor.model.dbobj.parent.actorRole is not "":
            parent_role = actor.model.dbobj.parent.actorRole

            # try to get the instance name from the args. Look for full actor name ('node.ssh') or just role (node)
            # if none of the two is available in the args, don't use instance name and
            # expect the parent service to be unique in the repo
            parent_name = args.get(actor.model.dbobj.parent.argKey, args.get(parent_role, ''))
            res = self.aysrepo.servicesFind(name=parent_name, actor='%s.*' % parent_role)
            res = [s for s in res if s.model.role == parent_role]
            if len(res) == 0:
                if actor.model.dbobj.parent.optional:
                    return None
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

            self.model.dbobj.parent.actorName = parentobj.model.dbobj.actorName
            self.model.dbobj.parent.key = parentobj.model.key
            self.model.dbobj.parent.serviceName = parentobj.name

            return parentobj

        return None

    def _initProducers(self, actor, args):

        for i, producer_model in enumerate(actor.model.dbobj.producers):
            producer_role = producer_model.actorRole

            instances = args.get(producer_model.argKey, args.get(producer_role, ""))

            if not j.data.types.list.check(instances):
                instances = [instances]

            for i in instances:
                res = self.aysrepo.servicesFind(name=i, actor='%s.*' % producer_role)
                res = [s for s in res if s.model.role == producer_role]

                if len(res) == 0:
                    if producer_model.minServices == 0:
                        continue

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
                # add the service we consumer in the producers list
                self.model.producerAdd(
                    actorName=producer_obj.model.dbobj.actorName,
                    serviceName=producer_obj.model.dbobj.name,
                    key=producer_obj.model.key)
                # add ourself to the consumers list of the producer
                producer_obj.model.consumerAdd(
                    actorName=self.model.dbobj.actorName,
                    serviceName=self.model.dbobj.name,
                    key=self.model.key)


        # add the parent to the producers
        if self.parent is not None:
            producer = self.model.producerAdd(
                actorName=self.parent.model.dbobj.actorName,
                serviceName=self.parent.model.dbobj.name,
                key=self.parent.model.key)

            # add ourself to the consumers list of the parent
            self.parent.model.consumerAdd(
                actorName=self.model.dbobj.actorName,
                serviceName=self.model.dbobj.name,
                key=self.model.key)

    def _check_args(self, actor, args):
        """ Checks whether if args are the same as in instance model """
        data = j.data.serializer.json.loads(self.model.dataJSON)
        for key, value in args.items():
            sanitized_key = j.data.hrd.sanitize_key(key)
            if sanitized_key in data and data[sanitized_key] != value:
                self.processChange(actor=actor, changeCategory="dataschema", args=args)
                break

    def loadFromFS(self, path):
        """
        get content from fs and load in object
        only for DR purposes, std from key value stor
        """
        self.logger.debug("load service from FS: %s" % path)
        if self.model is None:
            self.model = self.aysrepo.db.services.new()

        model_json = j.data.serializer.json.load(j.sal.fs.joinPaths(path, "service.json"))
        # for now we don't reload the actions codes.
        # when using distributed DB, the actions code could still be available
        del model_json['actions']
        self.model.dbobj = self.aysrepo.db.services.capnp_schema.new_message(**model_json)

        data_json = j.data.serializer.json.load(j.sal.fs.joinPaths(path, "data.json"))
        self.model.dbobj.data = j.data.capnp.getBinaryData(j.data.capnp.getObj(self.model.dbobj.dataSchema, args=data_json))
        # data_obj = j.data.capnp.getObj(self.model.dbobj.dataSchema, data_json)
        # self.model._data = data_obj

        # actions
        # relink actions from the actor to be sure we have good keys
        actor = self.aysrepo.actorGet(name=self.model.dbobj.actorName)
        actions = self.model.dbobj.init("actions", len(actor.model.dbobj.actions))
        counter = 0
        for action in actor.model.dbobj.actions:
            actionnew = actions[counter]
            actionnew.state = "new"
            actionnew.actionKey = action.actionKey
            actionnew.name = action.name
            actionnew.log = action.log
            actionnew.period = action.period
            counter += 1

        self.saveAll()

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

    def delete(self):
        """
        delete this service completly.
        remove it from db and from filesystem
        all the children of this service are going to be deleted too
        """
        # TODO should probably warn user relation may be broken

        for prod_model in self.model.producers:
            prod_model.consumerRemove(self)

        for cons_model in self.model.consumers:
            cons_model.producerRemove(self)

        for service in self.children:
            service.delete()

        self.model.delete()
        j.sal.fs.removeDirTree(self.path)

    @property
    def parent(self):
        if self.model.parent is not None:
            return self.model.parent.objectGet(self.aysrepo)
        return None

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
        producers = {}
        for prod_model in self.model.producers:

            if prod_model.role not in producers:
                producers[prod_model.role] = []

            result = self.aysrepo.servicesFind(name=prod_model.dbobj.name, actor=prod_model.dbobj.actorName)
            producers[prod_model.role].extend(result)

        return producers

    @property
    def consumers(self):
        consumers = {}
        for prod_model in self.model.consumers:

            if prod_model.role not in consumers:
                consumers[prod_model.role] = []

            result = self.aysrepo.servicesFind(name=prod_model.dbobj.name, actor=prod_model.dbobj.actorName)
            consumers[prod_model.role].extend(result)

        return consumers

    def isConsumedBy(self, service):
        consumers_keys = [model.key for model in self.model.consumers]
        return service.model.key in consumers_keys

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
                producers = producer.getProducersRecursive(producers=producers, callers=callers, action=action, producerRoles=producerRoles)
        return producers.symmetric_difference(callers)

    def printProducersRecursive(self, prefix=""):
        for role, producers2 in self.producers.items():
            # print ("%s%s"%(prefix,role))
            for producer in producers2:
                print("%s- %s" % (prefix, producer))
                producer.printProducersRecursive(prefix + "  ")


    def getConsumersRecursive(self, consumers=set(), callers=set(), action="", consumerRole="*"):
        for role, consumers_list in self.consumers.items():
            for consumer in consumers_list:
                if action == "" or action in consumer.model.actionsState.keys():
                    if consumerRole == "*" or consumer.model.role in consmersRole:
                        consumers.add(consumer)
                consumers = consumer.getConsumersRecursive(
                    consumers=consumers, callers=callers, action=action, consumerRole=consumerRole)
        return consumers.symmetric_difference(callers)

    def getConsumersWaiting(self, action='uninstall', consumersChanged=set(), scope=None):
        for consumer in self.getConsumersRecursive(set(), set()):
            # check that the action exists, no need to wait for other actions,
            # appart from when init or install not done

            if consumer.model.actionsState['init'] != "ok":
                consumersChanged.add(consumer)

            if consumer.model.actionsState['install'] != "ok":
                consumersChanged.add(consumer)

            if action not in consumer.model.actionsState.keys():
                continue

            if consumer.model.actionsState[action] != "ok":
                consumersChanged.add(consumer)

        if scope is not None:
            consumersChanged = consumersChanged.intersection(scope)

        return consumersChanged

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

        # add ourself to the consumers list of the producer
        service.model.consumerAdd(
            actorName=self.model.dbobj.actorName,
            serviceName=self.model.dbobj.name,
            key=self.model.key)

        self.saveAll()
        service.saveAll()

    @property
    def executor(self):
        return self._getExecutor()

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
            self.model.actionAdd(key=actor_action_pointer.actionKey, name=action_name)

        elif changeCategory.find('action_mod') != -1:
            # update state and pointer of the action pointer in service model
            action_name = changeCategory.split('action_mod_')[1]
            action_actor_pointer = actor.model.actions[action_name]
            service_action_pointer = self.model.actions[action_name]
            service_action_pointer.state = 'changed'
            service_action_pointer.actionKey = action_actor_pointer.actionKey

            # update the lastModDate of the action object
            action = j.core.jobcontroller.db.actions.get(key=service_action_pointer.actionKey)
            action.dbobj.lastModDate = j.data.time.epoch
            action.save()

        # execute the processChange method if it exists
        if 'processChange' in self.model.actions.keys():
            args.update({'changeCategory': changeCategory})
            job = self.getJob("processChange", args=args)
            args = job.executeInProcess()
            job.model.save()

        self.model.save()

    def input(self, args={}):
        job = self.getJob("input", args=args)
        job._service = self
        job.saveService = False  # this is done to make sure we don't save the service at this point !!!
        args = job.executeInProcess()
        job.model.actorName = self.model.dbobj.actorName
        job.model.save()
        return args

    def init(self):
        job = self.getJob(actionName="init")
        job.executeInProcess()
        job.model.save()
        return job

    def checkActions(self, actions):
        """
        will walk over all actions, and make sure the default are well set.

        """
        from IPython import embed
        print("DEBUG NOW checkactions")
        embed()
        raise RuntimeError("stop debug here")

    def scheduleAction(self, action, args={}, period=None, log=True, force=False):
        """
        Change the state of an action so it marked as need to be executed
        if the period is specified, also create a recurring period for the action
        """
        self.logger.info('schedule action %s on %s' % (action, self))
        if action not in self.model.actions:
            raise j.exceptions.Input(
                "Trying to schedule action %s on %s. but this action doesn't exist" % (action, self))

        action_model = self.model.actions[action]

        if action_model.state == 'disabled':
            raise j.exceptions.Input("Trying to schedule action %s on %s. but this action is disabled" % (action, self))

        if period is not None and period != '':
            # convert period to seconds
            if j.data.types.string.check(period):
                period = j.data.types.duration.convertToSeconds(period)
            elif j.data.types.int.check(period) or j.data.types.float.check(period):
                period = int(period)
            # save period into actionCode model
            action_model.period = period

        if not force and action_model.state == 'ok':
            self.logger.info("action %s already in ok state, don't schedule again" % action_model.name)
        else:
            action_model.state = 'scheduled'

        self.saveAll()

    def executeAction(self, action, args={}):
        if action[-1] == "_":
            return self.executeActionService(action)
        else:
            return self.executeActionJob(action, args)

    def executeActionService(self, action, args={}):
        # execute an action in process without creating a job
        # usefull for methods called very often.
        action_id = self.model.actions[action].actionKey
        action_model = j.core.jobcontroller.db.actions.get(action_id)
        action_with_lines = ("\n %s \n" % action_model.code)
        indented_action = '\n    '.join(action_with_lines.splitlines())
        complete_action = "def %s(%s): %s" % (action, action_model.argsText, indented_action)
        exec(complete_action)
        res = eval(action)(service=self, args=args)
        return res

    def executeActionJob(self, actionName, args={}, inprocess=False):
        self.logger.debug('execute action %s on %s' % (actionName, self))
        job = self.getJob(actionName=actionName, args=args)

        # inprocess means we don't want to create subprocesses for this job
        # used mainly for action called from other actions.
        if inprocess:
            job.model.dbobj.debug = True

        now = j.data.time.epoch
        p = job.execute()

        if job.model.dbobj.debug is True:
            return job

        while not p.isDone():
            time.sleep(0.5)
            p.sync()
            if p.new_stdout != "":
                self.logger.info(p.new_stdout)

        # just to make sure process is cleared
        p.wait()

        # if the action is a reccuring action, save last execution time in model
        if actionName in self.model.actionsRecurring:
            self.model.actionsRecurring[actionName].lastRun = now

        service_action_obj = self.model.actions[actionName]

        if p.state != 'success':
            job.model.dbobj.state = 'error'
            service_action_obj.state = 'error'
            # processError creates the logs entry in job object
            job._processError(p.error)
            # print error
            log = job.model.dbobj.logs[-1]
            print(job.str_error(log.log))
        else:
            job.model.dbobj.state = 'ok'
            service_action_obj.state = 'ok'

            log_enable = j.core.jobcontroller.db.actions.get(service_action_obj.actionKey).dbobj.log
            if log_enable:
                job.model.log(msg=p.stdout, level=5, category='out')
                job.model.log(msg=p.stderr, level=5, category='err')
            self.logger.info("job {} done sucessfuly".format(str(job)))

        job.model.save()
        job.service.saveAll()

        return job

    def getJob(self, actionName, args={}):
        action = self.model.actions[actionName]
        jobobj = j.core.jobcontroller.db.jobs.new()
        jobobj.dbobj.repoKey = self.aysrepo.model.key
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

    def _build_actions_chain(self, action):
        """
        this method returns a list of action that need to happens before the action passed in argument
        can start
        """
        ds = list()
        self.model._build_actions_chain(ds=ds)
        ds.reverse()
        return ds

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
