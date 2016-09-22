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
        self._producers = None
        self._name = name

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
        if actor.model.dbobj.parent.actorKey is not "":
            actor_name = actor.model.dbobj.parent.actorName
            actor_role = actor_name.split('.')[0]
            # try to get the instance name from the args. Look for full actor name ('node.ssh') or just role (node)
            # if none of the two is available in the args, don't use instance name and expect the parent service to be unique in the repo
            parent_name = args.get(actor_name, args.get(actor_role, None))
            res = self.aysrepo.servicesFind(name=parent_name, actor='%s.*' % actor_role)
            if len(res) == 0:
                raise j.exceptions.Input(message="could not find parent:%s for %s, found 0" %
                                         (actor_name, self), level=1, source="", tags="", msgpub="")
            elif len(res) > 1:
                raise j.exceptions.Input(message="could not find parent:%s for %s, found more than 1." %
                                         (actor_name, self), level=1, source="", tags="", msgpub="")
            parentobj = res[0]
            self._parent = parentobj
            fullpath = j.sal.fs.joinPaths(parentobj.path, skey)
            relpath = j.sal.fs.pathRemoveDirPart(fullpath, self.aysrepo.path)

            self.model.dbobj.parent.actorName = parentobj.model.dbobj.actorName
            self.model.dbobj.parent.key = parentobj.model.key
            self.model.dbobj.parent.serviceName = parentobj.model.dbobj.name

        else:
            relpath = j.sal.fs.joinPaths("services", skey)
        r.path = relpath

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
    def parents(self):
        raise NotImplemented("")
        # TODO: *1
        if self._parentChain is None:
            chain = []
            parent = self.parent
            while parent is not None:
                chain.append(parent)
                parent = parent.parent
            self._parentChain = chain
        return self._parentChain

    @property
    def parent(self):
        raise NotImplemented("")
        # TODO: *1
        if self._parent is None:
            if self.model.parent != "":
                self._parent = self.aysrepo.getServiceFromKey(
                    self.model.parent)
        return self._parent

    @property
    def producers(self):
        producers = {}
        for prod_model in self.model.producers:

            if prod_model.dbobj.actorName not in self._producers:
                self._producers[prod_model.dbobj.actorName] = []

            result = self.aysrepo.servicesFind(name=prod_model.dbobj.name, actor=prod_model.dbobj.actorName)
            for service in result:
                self._producers[prod_model.dbobj.actorName].append(service)

        return self._producers

    def remove_producer(self, role, instance):
        raise NotImplemented("")
        # TODO: *1
        key = "%s!%s" % (role, instance)
        self.model.remove_producer(role, instance)
        self._producers[role].remove(key)

    @property
    def executor(self):
        raise NotImplemented("")
        if self._executor is None:
            self._executor = self._getExecutor()
        return self._executor

    def processChange(self, item):
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
        if isinstance(service, str):
            return self.key == service
        return service.role == self.role and self.instance == service.instance

    def __hash__(self):
        return hash((self.instance, self.role))

    def __repr__(self):
        return "service:%s!%s" % (self.model.role, self.model.name)

    def __str__(self):
        return self.__repr__()

    # def _getDisabledProducers(self):
    #     producers = dict()
    #     for key, items in self.hrd.getDictFromPrefix("producer").items():
    #         producers[key] = [self.aysrepo.getServiceFromKey(
    #             item.strip(), include_disabled=True) for item in items]
    #     return producers
    #
    # def _getConsumers(self, include_disabled=False):
    #     consumers = list()
    #     services = j.atyourservice.findServices(
    #         include_disabled=True, first=False)
    #     for service in services:
    #         producers = service._getDisabledProducers(
    #         ) if include_disabled else service.producers
    #         if self.role in producers and self in producers[self.role]:
    #             consumers.append(service)
    #     return consumers
    #
    # def disable(self):
    #     self.stop()
    #     for consumer in self._getConsumers():
    #         candidates = self.aysrepo.findServices(role=self.role, first=False)
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
    # def reload(self):
    #     # reload instance.hrd
    #     hrdpath = j.sal.fs.joinPaths(self.path, "instance.hrd")
    #     if not j.sal.fs.exists(path=hrdpath):
    #         self._hrd == "EMPTY"
    #     self._hrd = j.data.hrd.get(path=hrdpath, prefixWithName=False)
    #
    #     # reload model if any
    #     model_path = j.sal.fs.joinPaths(self.path, "model.yaml")
    #     if j.sal.fs.exists(model_path):
    #         self._model = j.data.serializer.yaml.loads(
    #             j.sal.fs.fileGetContents(model_path))
    #
    #     self.model.load()

    # def _consumeFromSchema(self, args):
    #     raise NotImplemented()
    #
    #     if self.actor.schema is None:
    #         return
    #
    #     self.logger.debug('[_consumeFromSchema] args %s' % args)
    #
    #     # manipulate the HRD's to mention the consume's to producers
    #     consumes = self.actor.schema.consumeSchemaItemsGet()
    #     if consumes:
    #         for consumeitem in consumes:
    #             # parent exists
    #             role = consumeitem.consume_link
    #             consumename = consumeitem.name
    #
    #             instancenames = []
    #             if consumename in args:
    #                 # args[consumename] can be a list or a string, we need to
    #                 # convert it to a list
    #                 if type(args[consumename]) == str:
    #                     instancenames = [args[consumename]]
    #                 else:
    #                     instancenames = args[consumename]
    #
    #             ays_s = list()
    #             candidates = self.aysrepo.findServices(
    #                 role=consumeitem.consume_link)
    #             if len(candidates) > 0:
    #                 if len(instancenames) > 0:
    #                     ays_s = [
    #                         candidate for candidate in candidates if candidate.instance in instancenames]
    #                 else:
    #                     self.logger.debug(
    #                         '[_consumeFromSchema] No instance specificed for consumed service %s' % consumename)
    #                     ays_s = candidates
    #
    #             # autoconsume
    #             if len(candidates) < int(consumeitem.consume_nr_min) and consumeitem.auto:
    #                 for instance in range(len(candidates), int(consumeitem.consume_nr_min)):
    #                     consumable = self.aysrepo.new(
    #                         name=consumeitem.consume_link, instance='auto_%i' % instance, parent=self.parent)
    #                     ays_s.append(consumable)
    #
    #             if len(ays_s) > int(consumeitem.consume_nr_max):
    #                 raise j.exceptions.RuntimeError("Found too many services with role '%s' which we are relying upon for service '%s, max:'%s'" % (
    #                     role, self, consumeitem.consume_nr_max))
    #             if len(ays_s) < int(consumeitem.consume_nr_min):
    #                 msg = "Found not enough services with role '%s' which we are relying upon for service '%s, min:'%s'" % (
    #                     role, self, consumeitem.consume_nr_min)
    #                 if len(ays_s) > 0:
    #                     msg += "Require following instances:%s" % self.args[
    #                         consumename]
    #                 raise j.exceptions.RuntimeError(msg)
    #
    #             # if producer has been removed from service, we need to remove
    #             # it from the state
    #             to_consume = set(ays_s)
    #             current_producers = self.producers.get(
    #                 consumeitem.consume_link, [])
    #             to_unconsume = set(current_producers).difference(to_consume)
    #             for ays in to_consume:
    #                 self.model.consume(aysi=ays)
    #             for ays in to_unconsume:
    #                 self.model.remove_producer(ays.role, ays.instance)
    #         self.model.save()
    #
    # def consume(self, input):
    #     """
    #     @input is comma separate list of ayskeys or a Service object or list of Service object
    #
    #     ayskeys in format $domain|$name:$instance@role ($version)
    #
    #     example
    #     ```
    #     @input $domain|$name!$instance,$name2!$instance2,$name2,$role4
    #     ```
    #
    #     """
    #     if input is not None and input is not '':
    #         toConsume = set()
    #         if j.data.types.string.check(input):
    #             entities = [item for item in input.split(
    #                 ",") if item.strip() != ""]
    #             for entry in entities:
    #                 service = self.aysrepo.getServiceFromKey(entry.strip())
    #                 toConsume.add(service)
    #
    #         elif j.data.types.list.check(input):
    #             for service in input:
    #                 toConsume.add(service)
    #
    #         elif isinstance(input, Service):
    #             toConsume.add(input)
    #         else:
    #             raise j.exceptions.Input("Type of input to consume not valid. Only support list, string or Service object",
    #                                      category='AYS.consume', msgpub='Type of input to consume not valid. Only support list, string or Service object')
    #
    #         for ays in toConsume:
    #             self.model.consume(aysi=ays)

    # def getProducersRecursive(self, producers=set(), callers=set(), action="", producerRoles="*"):
    #     for role, producers2 in self.producers.items():
    #         for producer in producers2:
    #             if action == "" or producer.getAction(action) != None:
    #                 if producerRoles == "*" or producer.role in producerRoles:
    #                     producers.add(producer)
    #             producers = producer.getProducersRecursive(
    #                 producers=producers, callers=callers, action=action, producerRoles=producerRoles)
    #     return producers.symmetric_difference(callers)
    #
    # def printProducersRecursive(self, prefix=""):
    #     for role, producers2 in self.producers.items():
    #         # print ("%s%s"%(prefix,role))
    #         for producer in producers2:
    #             print("%s- %s" % (prefix, producer))
    #             producer.printProducersRecursive(prefix + "  ")
    #
    # def getProducersWaiting(self, action="install", producersChanged=set(), scope=None):
    #     """
    #     return list of producers which are waiting to be executing the action
    #     """
    #
    #     # print ("producerswaiting:%s"%self)
    #     for producer in self.getProducersRecursive(set(), set()):
    #         # check that the action exists, no need to wait for other actions,
    #         # appart from when init or install not done
    #
    #         if producer.state.getObject("init").state != "OK":
    #             producersChanged.add(producer)
    #
    #         if producer.state.getObject("install").state != "OK":
    #             producersChanged.add(producer)
    #
    #         if producer.getAction(action) is None:
    #             continue
    #
    #         actionrunobj = producer.state.getSetObject(action)
    #         # print (actionrunobj)
    #         if actionrunobj.state != "OK":
    #             producersChanged.add(producer)
    #
    #     if scope is not None:
    #         producersChanged = producersChanged.intersection(scope)
    #
    #     return producersChanged

    # def getNode(self):
    #     for parent in self.parents:
    #         if 'ssh' == parent.role:
    #             return parent
    #     return None
    #
    # def isOnNode(self, node=None):
    #     mynode = self.getNode()
    #     if mynode is None:
    #         return False
    #     return mynode.key == node.key
    #
    # def getTCPPorts(self, processes=None, *args, **kwargs):
    #     ports = set()
    #     if processes is None:
    #         processes = self.getProcessDicts()
    #     for process in self.getProcessDicts():
    #         for item in process.get("ports", []):
    #             if isinstance(item, str):
    #                 moreports = item.split(";")
    #             elif isinstance(item, int):
    #                 moreports = [item]
    #             for port in moreports:
    #                 if isinstance(port, int) or port.isdigit():
    #                     ports.add(int(port))
    #     return list(ports)
    #
    # def getPriority(self):
    #     processes = self.getProcessDicts()
    #     if processes:
    #         return processes[0].get('prio', 100)
    #     return 199
    #
    # def getProcessDicts(self, args={}):
    #     return getProcessDicts(self, args={})
    #
    # def _downloadFromNode(self):
    #     # if 'os' not in self.producers or self.executor is None:
    #     if not self.parent or self.parent.role != 'ssh':
    #         return
    #
    #     hrd_root = "/etc/ays/local/"
    #     remotePath = j.sal.fs.joinPaths(
    #         hrd_root, j.sal.fs.getBaseName(self.path), 'instance.hrd')
    #     dest = self.path.rstrip("/") + "/" + "instance.hrd"
    #     self.logger.info("downloading %s '%s'->'%s'" %
    #                      (self.key, remotePath, self.path))
    #     self.executor.download(remotePath, self.path)
    #
    # def _getExecutor(self):
    #     executor = None
    #     tocheck = [self]
    #     tocheck.extend(self.parents)
    #     for service in tocheck:
    #         if hasattr(service.actions, 'getExecutor'):
    #             executor = service.actions.getExecutor(service=service)
    #             return executor
    #     return j.tools.executor.getLocal()
    #
    # def log(self, msg, level=0):
    #     self.action_current.log(msg)
    #
    # def listChildren(self):
    #
    #     childDirs = j.sal.fs.listDirsInDir(self.path)
    #     childs = {}
    #     for path in childDirs:
    #         if path.endswith('__pycache__'):
    #             continue
    #         child = j.sal.fs.getBaseName(path)
    #         name, instance = child.split("!")
    #         if name not in childs:
    #             childs[name] = []
    #         childs[name].append(instance)
    #     return childs
    #
    # @property
    # def children(self):
    #     res = []
    #     for key, service in self.aysrepo.services.items():
    #         if service.parent == self:
    #             res.append(service)
    #     return res
    #
    # def isConsumedBy(self, service):
    #     if self.role in service.producers:
    #         for s in service.producers[self.role]:
    #             if s.key == self.key:
    #                 return True
    #     return False
    #
    # def get_consumers(self):
    #     return [service for service in list(self.aysrepo.services.values()) if self.isConsumedBy(service)]
    #
    # def getProducers(self, producercategory):
    #     if producercategory not in self.producers:
    #         raise j.exceptions.Input(
    #             "cannot find producer with category:%s" % producercategory)
    #     instances = self.producers[producercategory]
    #     return instances

    # @property
    # def action_methods_node(self):
    #     if self._action_methods_node is None or not self._rememberActions:
    #         if j.sal.fs.exists(path=self.actor.path_actions_node):
    #             action_methods_node = self._loadActions(self.actor.path_actions_node,"node")
    #         else:
    #             action_methods_node = j.atyourservice.getActionsBaseClassNode()()

    #         self._action_methods_node=action_methods_node

    #     return self._action_methods_node

    # def getAction(self, name, printonly=False):
    #     if name not in self._actionlog:
    #         action = self._setAction(name, printonly=printonly)
    #         print("new action:%s (get)" % action)
    #     else:
    #         action=self._actionlog[name]
    #     action.printonly = printonly
    #     self.action_current = action
    #     return action

    # def runAction(self,name,printonly=False):
    #     """
    #     look for action & run, there are no arguments
    #     """
    #     method=self._getActionMethodMgmt(name)
    #     if method==None:
    #         return None
    #     action=j.actions.add(method, kwargs={"ayskey":self.key}, die=True, stdOutput=False, \
    #             errorOutput=False, executeNow=True,force=True, showout=False, actionshow=True,selfGeneratorCode='selfobj=None')
    #     j.application.break_into_jshell("DEBUG NOW runaction")

    #     return action

    # def runActionNode(self,name,*args,**kwargs):
    #     """
    #     run on node, need to pass all arguments required
    #     there are no arguments given by default
    #     """
    #     method=self._getActionMethodNode(name)
    #     if method==None:
    #         return None
    #     j.application.break_into_jshell("DEBUG NOW runaction node")
    #     return action

    # def _getActionMethodMgmt(self,action):
    #     try:
    #         method=eval("self.action_methods_mgmt.%s"%action)
    #     except Exception as e:
    #         if str(e).find("has no attribute")!=-1:
    #             return None
    #         raise j.exceptions.RuntimeError(e)
    #     return method

    # def _getActionMethodNode(self,action):
    #     try:
    #         method=eval("self.action_methods_node.%s"%action)
    #     except Exception as e:
    #         if str(e).find("has no attribute")!=-1:
    #             return None
    #         raise j.exceptions.RuntimeError(e)
    #     return method

    # # ACTIONS
    # # def _executeOnNode(self, actionName, cmd=None, reinstall=False):
    # def _executeOnNode(self, actionName):
    #     if not self.parent or self.parent.role != 'ssh':
    #     # if 'os' not in self.producers or self.executor is None:
    #         return False
    #     self._uploadToNode()

    #     execCmd = 'source /opt/jumpscale8/env.sh; aysexec do %s %s %s' % (actionName, self.role, self.instance)

    #     executor = self.executor
    #     executor.execute(execCmd, die=True, showout=True)

    #     return True
