from JumpScale import j

from JumpScale.baselib.atyourservice81.Actor import Actor
from JumpScale.baselib.atyourservice81.Service import Service
from JumpScale.baselib.atyourservice81.Blueprint import Blueprint
from JumpScale.baselib.jobcontroller.Run import Run
from JumpScale.baselib.atyourservice81.models import ModelsFactory

import colored_traceback
colored_traceback.add_hook(always=True)


VALID_ACTION_STATE = ['new', 'installing', 'ok', 'error', 'disabled', 'changed']


class AtYourServiceRepo():

    def __init__(self, name, gitrepo, path, model=None):

        self._init = False

        self.indocker = j.atyourservice.indocker
        self.debug = j.atyourservice.debug
        self.logger = j.atyourservice.logger

        self._todo = []

        self.path = path

        self.git = gitrepo

        self.name = name

        self.db = ModelsFactory(self)
        if model is None:
            self.model = self.db.repo.find(path=path)[0]
        else:
            self.model = model

        j.atyourservice.loadActionBase()

    def destroy(self, uninstall=True):
        if uninstall:
            self.uninstall()
        j.sal.fs.removeDirTree(j.sal.fs.joinPaths(self.path, "actors"))
        j.sal.fs.removeDirTree(j.sal.fs.joinPaths(self.path, "services"))
        j.sal.fs.removeDirTree(j.sal.fs.joinPaths(self.path, "recipes"))  # for old time sake
        self.db.actor.destroy()
        self.db.service.destroy()
        self.model.delete()

# ACTORS

    def getActorClass(self):
        return Actor

    def actorCreate(self, name):
        """
        will look for name inside & create actor from it
        """
        actorTemplate = self.templateGet(name)
        actor = Actor(aysrepo=self, template=actorTemplate)
        return actor

    def actorGet(self, name, reload=False, die=False):
        actors = self.db.actor.find(name=name)
        if len(actors) == 1:
            obj = actors[0].objectGet(self)
        elif len(actors) > 1:
            raise j.exceptions.Input(message="ore then one actor find with this name:%s" % name, level=1, source="", tags="", msgpub="")
        elif len(actors) < 1:
            # checking if we have the actor on the file system
            actors_dir = j.sal.fs.joinPaths(self.path, 'actors')
            results = j.sal.fs.walkExtended(actors_dir, files=False, dirPattern=name)
            if len(results) == 1:
                actor = Actor(aysrepo=self, name=name)
            elif die:
                raise j.exceptions.Input(message="Could not find actor with name:%s" % name, level=1, source="", tags="", msgpub="")

            obj = self.actorCreate(name)

        if reload:
            obj.loadFromFS()

        return obj

    def actorGetByKey(self, key):
        return self.db.actor.get(key).objectGet(self)

    def actorExists(self, name):
        if name in self.actors:
            return True
        return False

    @property
    def actors(self):
        actors = {}
        for model in self.db.actor.find():
            if model.dbobj.state != "disabled":
                actors[model.dbobj.name] = model.objectGet(aysrepo=self)
        return actors

    def actorsFind(self, name="", version="", role=''):
        res = []
        if version != "":
            raise NotImplemented("actors find with version not implemented.")
        for item in self.db.actor.find(name=name):
            if not(name == "" or item.model.name == name):
                # no match continue
                continue
            if not (role == '' or item.model.role == role):
                # no match continue
                continue
            res.append(item)
        return res

# TEMPLATES

    @property
    def templates(self):
        """
        """
        templates = {}
        # need to link to templates of factory and then overrule with the local ones
        for key, template in j.atyourservice.actorTemplates.items():
            templates[key] = template

        # load local templates
        path = j.sal.fs.joinPaths(self.path, "actorTemplates")
        if j.sal.fs.exists(path):
            for template in j.atyourservice._actorTemplatesGet(self.git, path=path, aysrepo=self):
                # here we want to overrides the global templates with local one. so having duplicate name is normal
                templates[template.name] = template

        return templates

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
        services = []
        for service_model in self.db.service.find():
            if service_model.dbobj.state != "disabled":
                services.append(service_model.objectGet(aysrepo=self))
        return services

    def serviceGet(self, role, instance, key=None, die=True):
        """
        Return service indentifier by role and instance or key
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
        return objs[0].objectGet(self)

    def serviceGetByKey(self, key):
        return self.db.service.get(key=key).objectGet(self)

    @property
    def serviceKeys(self):
        keys = []
        for s in self.services:
            keys.append(s.model.key)
        return keys

    @property
    def servicesTree(self):
        # TODO: implement, needs to come from db now
        raise RuntimeError()

        if self._servicesTree:
            return self._servicesTree

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
        if state not in VALID_ACTION_STATE:
            raise j.exceptions.Input(message='%s is not a valid state. Should one of %s' %
                                     (state, ', '.join(VALID_ACTION_STATE)))


        if "install" in actions:
            if "init" not in actions:
                actions.insert(0, "init")

        for action in actions:
            for service in self.services:

                if role != "" and service.model.role != role:
                    continue
                if instance != "" and service.name != instance:
                    continue
                try:
                    action_obj = service.model.actions[action]
                    action_obj.state = state
                    service.save()
                except KeyError:
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
        for service_model in self.db.service.find(name=name, actor=actor, state=state, parent=parent, producer=producer):
            if hasAction != "" and hasAction not in service_model.actionsState.keys():
                continue

            if includeDisabled is False and service_model.dbobj.state == "disabled":
                continue

            res.append(service_model.objectGet(self))
        if first:
            if len(res) == 0:
                raise j.exceptions.Input("cannot find service %s|%s:%s" % (self.name, actor, name), "ays.servicesFind")
            return res[0]
        return res

# BLUEPRINTS

    def _load_blueprints(self):
        bps = {}
        bpdir = j.sal.fs.joinPaths(self.path, "blueprints")
        if j.sal.fs.exists(path=bpdir):
            items = j.sal.fs.listFilesInDir(bpdir)
            for path in items:
                if path not in bps:
                    bps[path] = Blueprint(self, path=path)
        return bps

    @property
    def blueprints(self):
        """
        only shows the ones which are on predefined location
        """
        bps = []
        for path, bp in self._load_blueprints().items():
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
        for path, bp in self._load_blueprints.items():
            if bp.active is False:
                bps.append(bp)
        bps = sorted(bps, key=lambda bp: bp.name)
        return bps

    def blueprintExecute(self, path="", content="", role="", instance=""):
        if path == "" and content == "":
            for bp in self.blueprints:
                bp.load(role=role, instance=instance)
        else:
            bp = Blueprint(self, path=path, content=content)
            # self._blueprints[bp.path] = bp
            bp.load(role=role, instance=instance)

        self.init(role=role, instance=instance)

        print("blueprint done")

    def blueprintGet(self, path):
        for bp in self.blueprints:
            if bp.path == path:
                return bp
        return Blueprint(self, path)

# RUN related

    def runFindActionScope(self, action, role="", instance="", producerRoles="*"):
        """
        find all services from role & instance and their producers
        only find producers wich have at least one of the actions
        """
        # create a scope in which we need to find work
        producerRoles = self._processProducerRoles(producerRoles)
        scope = set(self.servicesFind(actor="%s.*" % role, name=instance, hasAction=action))
        for service in scope:
            producer_candidates = service.getProducersRecursive(
                producers=set(), callers=set(), action=action, producerRoles=producerRoles)
            if producerRoles != '*':
                producer_valid = [item for item in producer_candidates if item.model.role in producerRoles]
            else:
                producer_valid = producer_candidates
            scope = scope.union(producer_valid)
        return scope

    def _processProducerRoles(self, producerroles):
        if j.data.types.string.check(producerroles):
            if producerroles == "*":
                return "*"
            elif producerroles == "":
                producerroles = []
            elif producerroles.find(",") != -1:
                producerroles = [item for item in producerroles.split(",") if item.strip() != ""]
            else:
                producerroles = [producerroles.strip()]
        return producerroles

    # def runGet(self, role="", instance="", action="install", force=False, producerRoles="*", data={}, key=0, simulate=False, debug=False, profile=False):
    #     """
    #     get a new run
    #     if key !=0 then the run will be loaded from DB
    #     """
    #
    #     if key != 0:
    #         run_model = j.core.jobcontroller.db.run.get(key)
    #         return run_model.objectGet()
    #
    #     producerRoles = self._processProducerRoles(producerRoles)
    #     if action not in ["init"]:
    #         for s in self.services:
    #             if s.model.actionsState['init'] not in ["new", "ok", "changed", "scheduled"]:
    #                 error_msg = "Cannot get run: %s:%s:%s because found a service not properly inited yet.\n%s\n please rerun ays init" % (
    #                     role, instance, action, s)
    #                 self.logger.error(error_msg)
    #                 raise j.exceptions.Input(error_msg, msgpub=error_msg)
    #
    #     if force:
    #         self.serviceSetState(actions=[action], role=role, instance=instance, state="scheduled")
    #
    #     actions = j.atyourservice.baseActions['']._build_actions_chain(action)
    #
    #     run = j.core.jobcontroller.newRun(simulate=simulate)
    #     for action0 in actions:
    #         scope = self.runFindActionScope(action=action0, role=role, instance=instance, producerRoles=producerRoles)
    #         todo = self._findTodo(action=action0, scope=scope, run=run, producerRoles=producerRoles)
    #         while todo != []:
    #             newStep = True
    #             for service in todo:
    #                 if service.model.actionsState[action0] not in ['ok', 'disabled']:
    #                     print("DO:%s %s" % (action0, service))
    #                     if newStep:
    #                         step = run.newStep()
    #                         newStep = False
    #                     job = service.getJob(action0, args=data)
    #                     job.model.dbobj.profile = profile
    #                     if profile:
    #                         debug = True
    #                     job.model.dbobj.debug = debug
    #                     step.addJob(job)
    #
    #                 if service in scope:
    #                     scope.remove(service)
    #
    #             todo = self._findTodo(action0, scope=scope, run=run, producerRoles=producerRoles)
    #
    #     # these are destructive actions, they need to happens in reverse order
    #     # in the dependency tree
    #     if action in ['uninstall', 'removedata', 'cleanup', 'halt', 'stop']:
    #         run.reverse()
    #
    #     return run

    def _findTodo(self, action, scope, run, producerRoles):
        if action == "" or action is None:
            raise j.exceptions.Input("action cannot be empty")

        if scope == []:
            return []

        todo = []
        waiting = False
        for service in scope:
            if run.hasServiceForAction(service, action):
                continue
            producersWaiting = service.getProducersRecursive(
                producers=set(), callers=set(), action=action, producerRoles=producerRoles)
            # remove the ones which are already in previous runs
            producersWaiting = [item for item in producersWaiting if run.hasServiceForAction(item, action) is False]
            # remove action that has alredy status ok
            producersWaiting = [item for item in producersWaiting if item.model.actionsState[action] != "ok"]

            if len(producersWaiting) == 0:
                todo.append(service)

        if todo == [] and waiting:
            raise RuntimeError(
                "cannot find todo's for action:%s in scope:%s.\n\nDEPENDENCY ERROR: could not resolve dependency chain." % (action, scope))
        return todo

    def runsList(self):
        """
        list Runs on repo
        """
        runs = j.core.jobcontroller.db.run.find()
        return runs

    def findScheduledActions(self):
        """
        Walk over all servies and look for action with state scheduled.
        It then creates actions chains for all schedules actions.
        """
        to_execute = {}
        for service in self.services:
            for action, state in service.model.actionsState.items():
                if state == 'scheduled':
                    if service not in to_execute:
                        to_execute[service] = [action]
                    else:
                        to_execute[service].append(action)

        result = {}
        for service, actions in to_execute.items():
            result[service] = []

            for action in actions:
                result[service].append(service._build_actions_chain(action))

        return result

    def createGlobalRun(self, data={}, simulate=False, debug=False, profile=False):
        """
        Create a run from all the scheduled actions in the repository.
        """
        run = j.core.jobcontroller.newRun(simulate=simulate)

        scheduled_actions = self.findScheduledActions()
        total_actions_set = set()

        for _, actions_list in scheduled_actions.items():

            for actions in actions_list:
                for action in actions:
                    total_actions_set.add(action)

                    scope = self.runFindActionScope(action, role="", instance="", producerRoles="*")
                    todo = self._findTodo(action=action, scope=scope, run=run, producerRoles="*")

                    while todo != []:
                        newStep = True
                        for service in todo:
                            if service.model.actionsState[action] not in ['ok', 'disabled']:
                                if newStep:
                                    step = run.newStep()
                                    newStep = False

                                job = service.getJob(action, args={})
                                job.model.dbobj.profile = False
                                if job.model.dbobj.profile:
                                    debug = True
                                job.model.dbobj.debug = debug

                                step.addJob(job)

                            if service in scope:
                                scope.remove(service)

                        todo = self._findTodo(action, scope=scope, run=run, producerRoles="*")

        # FIXME: this is not correct behavior
        # these are destructive actions, they need to happens in reverse order in the dependency tree
        if total_actions_set.isdisjoint(set(['uninstall', 'removedata', 'cleanup', 'halt', 'stop'])) is False:
            run.reverse()

        return run

# ACTIONS

    def init(self, role="", instance="", hasAction="", includeDisabled=False, data=""):
        for service in self.servicesFind(name=instance, actor='%s.*' % role, hasAction=hasAction, includeDisabled=includeDisabled):
            self.logger.info('init service: %s' % service)
            service.init()

        print("init done")

# Git management

    def commit(self, message="", branch="master", push=True):
        if message == "":
            message = "log changes for repo:%s" % self.name
        if branch != "master":
            self.git.switchBranch(branch)

        self.git.commit(message, True)

        if push:
            print("PUSH")

    def __str__(self):
        return("aysrepo:%s" % (self.path))

    __repr__ = __str__

    def __lt__(self, other):
        return self.path < other.path
