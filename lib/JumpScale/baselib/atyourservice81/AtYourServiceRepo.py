from JumpScale import j

from JumpScale.baselib.atyourservice81.Actor import Actor
from JumpScale.baselib.atyourservice81.Service import Service
from JumpScale.baselib.atyourservice81.Blueprint import Blueprint
from JumpScale.baselib.atyourservice81.AYSRun import AYSRun
from JumpScale.baselib.atyourservice81.models import ModelsFactory

import colored_traceback
colored_traceback.add_hook(always=True)


VALID_ACTION_STATE = ['new', 'installing', 'ok', 'error', 'disabled', 'changed,']


class AtYourServiceRepo():

    def __init__(self, name, gitrepo, path):

        self._init = False

        self.indocker = j.atyourservice.indocker
        self.debug = j.atyourservice.debug
        self.logger = j.atyourservice.logger

        self._todo = []

        self.path = path

        self.git = gitrepo

        self.name = name

        self._blueprints = {}
        self._templates = {}
        self._actors = {}

        self.db = ModelsFactory(self)

    def _doinit(self):
        if self._actors == {}:
            self.actors  # will load it

    def reset(self):
        # self._db.reload()
        j.dirs._ays = None
        # self._services = {}
        self._actors = {}
        self._templates = {}
        # self._reposDone = {}
        self._todo = []
        self._blueprints = {}
        # self._load_blueprints()
        # self._servicesTree = {}

    def destroy(self, uninstall=True):
        if uninstall:
            self.uninstall()
        j.sal.fs.removeDirTree(j.sal.fs.joinPaths(self.path, "actors"))
        j.sal.fs.removeDirTree(j.sal.fs.joinPaths(self.path, "services"))
        j.sal.fs.removeDirTree(j.sal.fs.joinPaths(self.path, "recipes"))  # for old time sake
        self.db.destroy()

# ACTORS

    def getActorClass(self):
        return Actor

    def actorCreate(self, name):
        """
        will look for name inside & create actor from it
        """
        actorTemplate = self.templateGet(name)
        actor = Actor(aysrepo=self, template=actorTemplate)
        actor.model.save()
        self._actors[actor.model.name] = actor
        return actor

    def actorGet(self, name, reload=False, die=False):
        if reload:
            self.reset()
        if name in self.actors:
            obj = self.actors[name]
        else:
            if die:
                raise j.exceptions.Input(message="Could not find actor with name:%s" %
                                         name, level=1, source="", tags="", msgpub="")
            obj = self.actorCreate(name)
        if reload:
            obj.loadFromFS()
        return obj

    def actorExists(self, name):
        if name in self.actors:
            return True
        return False

    @property
    def actors(self):
        if self._actors == {}:
            for item in self.db.actor.find():
                res = item.objectGet(aysrepo=self)
                if res.model.dbobj.state != "disabled":
                    self._actors[res.model.dbobj.name] = res
        return self._actors

    def actorsFind(self, name="", version="", role=''):
        res = []
        if version != "":
            raise NotImplemented("actors find with version not implemented.")
        for item in self.actors:
            if not(name == "" or item.name == name):
                # no match continue
                continue
            if not (role == '' or item.role == role):
                # no match continue
                continue
            res.append(item)
        return res

# TEMPLATES

    @property
    def templates(self):
        """
        """
        if self._templates == {}:
            # need to link to templates of factory and then overrule with the
            # local ones
            for key, template in j.atyourservice.actorTemplates.items():
                self._templates[key] = template

        # load local templates
        path = j.sal.fs.joinPaths(self.path, "actortemplates")
        if j.sal.fs.exists(path):
            for template in j.atyourservice._actorTemplatesGet(self.git, path=path, aysrepo=self):
                # here we want to overrides the global templates with local one. so having duplicate name is normal
                self._templates[template.name] = template

        return self._templates

    def templateGet(self, name, die=True):
        """
        @param first means, will only return first found template instance
        """
        if name in self.templates:
            return self.templates[name]
        if die:
            raise j.exceptions.Input(
                "Cannot find template with name:%s" % name)

    def templateExists(self, name):
        if self.templateGet(name, die=False) is None:
            return False
        return True

    def actorTemplatesFind(self, name="", domain="", role=''):
        res = []
        for template in self.templates:
            if not(name == "" or template.name == name):
                # no match continue
                continue
            if not(domain == "" or template.domain == domain):
                # no match continue
                continue
            if not (role == '' or template.role == role):
                # no match continue
                continue
            res.append(template)
        return res

# SERVICES

    def getServiceClass(self):
        return Service

    @property
    def services(self):
        services = {}
        for item in self.db.service.find():
            res = item.objectGet(aysrepo=self)
            if res.model.dbobj.state != "disabled":
                services[res.model.dbobj.name] = res
        return services

    def serviceGet(self, role, instance, die=True):
        """
        Return service indentifier by role and instance
        throw error if service is not found or if more than one service is found
        """
        if role.strip() == "" or instance.strip() == "":
            raise j.exceptions.Input("role and instance cannot be empty.")

        objs = self.db.service.find(actor="%s.*" % role, name=instance)
        if len(objs) == 0:
            if die:
                raise j.exceptions.Input(message="Cannot find service %s:%s" %
                                         (role, instance), level=1, source="", tags="", msgpub="")
            return None
        return objs[0]

    @property
    def serviceKeys(self):
        keys = []
        for s in self.services.values():
            keys.append(s.model.key)
        return keys

    @property
    def servicesTree(self):
        # TODO: implement, needs to come from db now
        raise RuntimeError()

        if self._servicesTree:
            return self._servicesTree
        self._doinit()
        producers = []
        parents = {"name": "sudoroot", "children": []}
        for root in j.sal.fs.walk(j.dirs.ays, recurse=1, pattern='*state.yaml', return_files=1, depth=2):
            servicekey = j.sal.fs.getBaseName(j.sal.fs.getDirName(root))
            service = self.services.get(servicekey)
            for _, producerinstances in service.producers.items():
                for producer in producerinstances:
                    producers.append([child.key, producer.key])
            parents["children"].append(self._nodechildren(
                service, {"children": [], "name": servicekey}, producers))
        self._servicesTree['parentchild'] = parents
        self._servicesTree['producerconsumer'] = producers
        return self._servicesTree

    def serviceSetState(self, actions=[], role="", instance="", state="new"):
        """
        get run with self.runGet...

        will not mark if state in skipIfIn

        """
        # import ipdb; ipdb.set_trace()
        if state not in VALID_ACTION_STATE:
            raise j.exceptions.Input(message='%s is not a valid state. Should one of %s' % (state, ', '.join(VALID_ACTION_STATE)))

        self._doinit()
        if "install" in actions:
            if "init" not in actions:
                actions.insert(0, "init")

        for action in actions:
            for key, service in self.services.items():

                if role != "" and service.role != role:
                    continue
                if instance != "" and service.instance != instance:
                    continue
                try:
                    action_obj = service.getActionObj(action)
                    action_obj.state = state
                    service.save()
                except j.exceptions.Input:
                    # mean action with this name doesn't exist
                    continue

    def servicesFind(self, name="", actor="", state="", parent="", producer="", hasAction="",
                     includeDisabled=False, first=False):
        """
        @param name can be the full name e.g. myappserver or a prefix but then use e.g. myapp.*
        @param actor can be the full name e.g. node.ssh or role e.g. node.*
                            (but then need to use the .* extension, which will match roles)
        @param parent is in form $actorName!$instance
        @param producer is in form $actorName!$instance

        @param state:
            new
            installing
            ok
            error
            disabled
            changed
        """
        res = []

        for aysi in self.db.service.find(name=name, actor=actor, state=state, parent=parent, producer=producer):

            if hasAction != "" and aysi.getAction(hasAction) is None:
                continue

            if includeDisabled is False and aysi.dbobj.state == "disabled":
                continue

            res.append(aysi.objectGet(self))
        if first:
            if len(res) == 0:
                raise j.exceptions.Input("cannot find service %s|%s:%s" % (self.name, actor, name), "ays.servicesFind")
            return res[0]
        return res

# BLUEPRINTS

    def _load_blueprints(self):
        bpdir = j.sal.fs.joinPaths(self.path, "blueprints")
        if j.sal.fs.exists(path=bpdir):
            items = j.sal.fs.listFilesInDir(bpdir)
            for path in items:
                if path not in self._blueprints:
                    self._blueprints[path] = Blueprint(self, path=path)

    @property
    def blueprints(self):
        """
        only shows the ones which are on predefined location
        """
        bps = []
        for path, bp in self._blueprints.items():
            if bp.active:
                bps.append(bp)

        bps = sorted(bps, key=lambda bp: bp.name)
        return bps

    @property
    def blueprintsDisabled(self):
        """
        Show the disabled blueprints
        """
        bps = []
        for path, bp in self._blueprints.items():
            if bp.active == False:
                bps.append(bp)
        bps = sorted(bps, key=lambda bp: bp.name)
        return bps

    def blueprintExecute(self, path="", content="", role="", instance=""):
        self._doinit()
        self._load_blueprints()
        if path == "" and content == "":
            for bp in self.blueprints:
                bp.load(role=role, instance=instance)
        else:
            bp = Blueprint(self, path=path, content=content)
            if bp.path not in self._blueprints:
                self._blueprints[bp.path] = bp
            bp.load(role=role, instance=instance)

        self.init(role=role, instance=instance)
        print("blueprint done")

    def blueprintGet(self, path):

        self._doinit()
        for bp in self.blueprints:
            if bp.path == path:
                return bp
        return Blueprint(self, path)

# RUN related

    # def runFindActionScope(self, action, role="", instance="", producerRoles="*"):
    #     """
    #     find all services from role & instance and their producers
    #     only find producers wich have at least one of the actions
    #     """
    #     # create a scope in which we need to find work
    #     producerRoles = self._processProducerRoles(producerRoles)
    #     scope = set(self.servicesFind(
    #         role=role, instance=instance, hasAction=action))
    #     for service in scope:
    #         producer_candidates = service.getProducersRecursive(
    #             producers=set(), callers=set(), action=action, producerRoles=producerRoles)
    #         if producerRoles != '*':
    #             producer_valid = [
    #                 item for item in producer_candidates if item.role in producerRoles]
    #         else:
    #             producer_valid = producer_candidates
    #         scope = scope.union(producer_valid)
    #     return scope
    #
    # def _processProducerRoles(self, producerroles):
    #     if j.data.types.string.check(producerroles):
    #         if producerroles == "*":
    #             return "*"
    #         elif producerroles == "":
    #             producerroles = []
    #         elif producerroles.find(",") != -1:
    #             producerroles = [item for item in producerroles.split(
    #                 ",") if item.strip() != ""]
    #         else:
    #             producerroles = [producerroles.strip()]
    #     return producerroles
    #
    # @property
    # def runs(self):
    #     from IPython import embed
    #     print("DEBUG NOW do")
    #     embed()
    #
    #     runs = AYSRun(self).list()
    #     return runs
    #
    # # def getSource(self, hash):
    # #     raise j.exceptions.RuntimeError("should not be like thios")
    # #     return AYSRun(self).getFile('source', hash)
    #
    # # def getHRD(self, hash):
    # #     raise j.exceptions.RuntimeError("should not be like thios")
    # #     return AYSRun(self).getFile('hrd', hash)
    #
    # def runGet(self, role="", instance="", action="install", force=False, producerRoles="*", data=None, id=0, simulate=False):
    #     """
    #     get a new run
    #     if id !=0 then the run will be loaded from DB
    #     """
    #     self._doinit()
    #
    #     if id != 0:
    #         run = AYSRun(self, id=id)
    #         return run
    #
    #     producerRoles = self._processProducerRoles(producerRoles)
    #
    #     if action not in ["init"]:
    #         for key, s in self.services.items():
    #             if s.state.get("init") not in ["OK", "DO"]:
    #                 error_msg = "Cannot get run: %s:%s:%s because found a service not properly inited yet.\n%s\n please rerun ays init" % (role, instance, action, s)
    #                 self.logger.error(error_msg)
    #                 raise j.exceptions.Input(error_msg, msgpub=error_msg)
    #     if force:
    #         self.setState(actions=[action], role=role,
    #                       instance=instance, state="DO")
    #
    #     if action == "init":
    #         actions = ["init"]
    #     else:
    #         actions = ["install", action]
    #
    #     run = AYSRun(self, simulate=simulate)
    #     for action0 in actions:
    #         scope = self.runFindActionScope(action=action0, role=role, instance=instance, producerRoles=producerRoles)
    #         todo = self._findTodo(action=action0, scope=scope, run=run, producerRoles=producerRoles)
    #         while todo != []:
    #             newstep = True
    #             for service in todo:
    #                 if service.state.get(action0, die=False) != "OK":
    #                     print("DO:%s %s" % (action, service))
    #                     if newstep:
    #                         step = run.newStep(action=action0)
    #                         newstep = False
    #                     step.addService(service)
    #                 if service in scope:
    #                     scope.remove(service)
    #             todo = self._findTodo(action0, scope=scope, run=run, producerRoles=producerRoles)
    #
    #     # these are destructive actions, they need to happens in reverse order
    #     # in the dependency tree
    #     if action in ['uninstall', 'removedata', 'cleanup', 'halt', 'stop']:
    #         run.reverse()
    #
    #     return run
    #
    # def _findTodo(self, action, scope, run, producerRoles):
    #     if action == "" or action is None:
    #         raise RuntimeError("action cannot be empty")
    #     if scope == []:
    #         return []
    #     todo = list()
    #     waiting = False
    #     for service in scope:
    #         if run.exists(service, action):
    #             continue
    #         producersWaiting = service.getProducersRecursive(
    #             producers=set(), callers=set(), action=action, producerRoles=producerRoles)
    #         # remove the ones which are already in previous runs
    #         producersWaiting = [
    #             item for item in producersWaiting if run.exists(item, action) == False]
    #         producersWaiting = [item for item in producersWaiting if item.state.get(
    #             action, die=False) != "OK"]
    #
    #         if len(producersWaiting) == 0:
    #             todo.append(service)
    #         elif j.application.debug:
    #             waiting = True
    #
    #     if todo == [] and waiting:
    #         raise RuntimeError(
    #             "cannot find todo's for action:%s in scope:%s.\n\nDEPENDENCY ERROR: could not resolve dependency chain." % (action, scope))
    #     return todo
    #
    # def _getChangedServices(self, action=None):
    #     changed = list()
    #     if not action:
    #         actions = ["install", "stop", "start", "monitor", "halt", "check_up", "check_down",
    #                    "check_requirements", "cleanup", "data_export", "data_import", "uninstall", "removedata"]
    #     else:
    #         actions = [action]
    #     for _, service in self.services.items():
    #         if [service for action in actions if action in list(service.action_methods.keys()) and service.state.get(action, die=False) == 'CHANGED']:
    #             changed.append(service)
    #             for producers in [producers for _, producers in service.producers.items()]:
    #                 changed.extend(producers)
    #     return changed

# ACTIONS

    def init(self, role="", instance="", hasAction="", include_disabled=False, data=""):
        self._doinit()
        if role == "" and instance == "":
            self.reset()

        self.serviceSetState(actions=["init"], role=role, instance=instance, state="new")

        # FIXME: what the goal here ?
        # for key, actor in self.actors.items():
        #     if role != "" and actor.role == role:
        #         continue
        #     actor.init()
        #     for inst in actor.listInstances():
        #         service = actor.aysrepo.getService(role=actor.role, instance=inst, die=False)
        #         print("RESETTING SERVICE roles %s inst %s instance %s " % (actor.role, inst, instance))
        #         service.update_hrd()
        #
        #     #actor.newInstance(instance=key, args={})

        # run = self.runGet(role=role, instance=instance, data=data, action="init")
        # run.execute()

        print("init done")

    # def commit(self, message="", branch="master", push=True):
    #     self._doinit()
    #     if message == "":
    #         message = "log changes for repo:%s" % self.name
    #     if branch != "master":
    #         self.git.switchBranch(branch)
    #
    #     self.git.commit(message, True)
    #
    #     if push:
    #         print("PUSH")
    #         self.git.push()
    #
    # def update(self, branch="master"):
    #     j.atyourservice.updateTemplates()
    #     if branch != "master":
    #         self.git.switchBranch(branch)
    #     self.git.pull()
    #
    # def install(self, role="", instance="", force=True, producerRoles="*"):
    #     self._doinit()
    #     if force:
    #         self.setState(actions=["install"], role=role,
    #                       instance=instance, state='DO')
    #
    #     run = self.runGet(action="install", force=force)
    #     print("RUN:INSTALL")
    #     print(run)
    #     run.execute()
    #
    # def uninstall(self, role="", instance="", force=True, producerRoles="*", printonly=False):
    #     self._doinit()
    #     if force:
    #         self.setState(actions=["stop", "uninstall"],
    #                       role=role, instance=instance, state='DO')
    #
    #     run = self.runGet(action="stop", force=force)
    #     print("RUN:STOP")
    #     print(run)
    #     if not printonly:
    #         run.execute()
    #
    #     run = self.runGet(role=role, instance=instance,
    #                       action="uninstall", force=force)
    #     print("RUN:UNINSTALL")
    #     print(run)
    #     if not printonly:
    #         run.execute()
    #     run.execute()

    def __str__(self):
        return("aysrepo:%s" % (self.name))

    __repr__ = __str__
