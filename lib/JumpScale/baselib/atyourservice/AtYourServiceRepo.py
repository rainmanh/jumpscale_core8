from JumpScale import j

from JumpScale.baselib.atyourservice.Actor import Actor
# from JumpScale.baselib.atyourservice.Service import Service, loadmodule
# from JumpScale.baselib.atyourservice.ActionsBaseNode import ActionsBaseNode
# from JumpScale.baselib.atyourservice.ActionsBase import ActionsBase
# from JumpScale.baselib.atyourservice.actorTemplate import actorTemplate
# from JumpScale.baselib.atyourservice.ActionMethodDecorator import ActionMethodDecorator
from JumpScale.baselib.atyourservice.Blueprint import Blueprint
from JumpScale.baselib.atyourservice.AYSRun import AYSRun
from JumpScale.baselib.atyourservice.Service import Service
# from AYSdb import *

import colored_traceback
colored_traceback.add_hook(always=True)


class AtYourServiceRepo():

    def __init__(self, name, gitrepo, path):

        self._init = False

        # self._services = {}
        self._actors = {}

        self._templates = {}

        self.indocker = j.atyourservice.indocker
        self.debug = j.atyourservice.debug
        self.logger = j.atyourservice.logger

        self._todo = []

        self.path = path

        self.git = gitrepo

        self._db = None

        self.name = name

        self._blueprints = {}

        # self._roletemplates = dict()
        self._servicesTree = {}


# INIT

    def _doinit(self):
        pass

    def reset(self):
        # self._db.reload()
        j.dirs._ays = None
        self._services = {}
        self._actors = {}
        self._templates = {}
        # self._reposDone = {}
        self._todo = []
        self._blueprints = {}
        # self._load_blueprints()
        self._servicesTree = {}

    def destroy(self, uninstall=True):
        if uninstall:
            self.uninstall()
        j.sal.fs.removeDirTree(j.sal.fs.joinPaths(self.path, "actors"))
        j.sal.fs.removeDirTree(j.sal.fs.joinPaths(self.path, "services"))
        j.sal.fs.removeDirTree(j.sal.fs.joinPaths(self.path, "recipes"))  # for old time sake
        self.db.destroy()

    @property
    def db(self):
        if not self._db:
            self._db = j.atyourservice.db.getDB('ays')
        return self._db

# ACTORS

    def actorCreate(self, name):
        """
        will look for name inside & create actor from it
        """
        actorTemplate = self.templateGet(name)
        actor = Actor(self, actorTemplate)
        self._actors[actor.name] = actor
        return actor

    def actorGet(self, name, reload=False):
        if name in self._actors:
            obj = self._actors[name]
        obj = self.actorCreate(name)
        #@TODO: reload
        return obj

    def actorExists(self, name):
        if name in self._actors:
            return True
        return j.atyourservice.db.actor.exists(name)

    @property
    def actors(self):
        self._doinit()
        if not self._actors:
            from IPython import embed
            print("DEBUG NOW actors")
            embed()
            raise RuntimeError("stop debug here")
        return self._actors

    def actorsFind(self, name="", version="", role=''):
        res = []
        domain = "ays"
        for template in self.actors:
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

# TEMPLATES

    @property
    def templates(self):
        """
        """
        self._doinit()
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
        if self.templateGet(name, die=False) == None:
            return False
        return True

# SERVICES

    def serviceGet(self, role, instance, die=True):
        """
        Return service indentifier by domain,name and instance
        throw error if service is not found or if more than one service is found
        """
        if role.strip() == "" or instance.strip() == "":
            raise j.exceptions.Input("role or instance cannot be empty.")
        key = "%s!%s" % (role, instance)
        if key in self.services:
            return self.services[key]
        if die:
            raise j.exceptions.Input("Cannot get ays service '%s', did not find" % key, "ays.getservice")
        else:
            return None

        return res[0]

    def serviceGetFromKey(self, key):
        """
        key in format $reponame!$name!$instance@role ($version)

        """
        if key.count("!") == 2:
            reponame, role, instance = key.split("!")
        else:
            role, instance = key.split("!")
        return self.getService(instance=instance, role=role, die=True)

    @property
    def services(self):
        self._doinit()
        if self._services == {}:
            services_path = j.sal.fs.joinPaths(self.path, "services")
            if not j.sal.fs.exists(services_path):
                return {}
            for hrd_path in j.sal.fs.listFilesInDir(services_path, recursive=True, filter="state.yaml",
                                                    case_sensitivity='os', followSymlinks=True, listSymlinks=False):
                service_path = j.sal.fs.getDirName(hrd_path)
                service = Service(self, path=service_path, args=None)
                self._services[service.key] = service
        return self._services

    @property
    def servicesTree(self):
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

    def serviceSetState(self, actions=[], role="", instance="", state="DO"):
        """
        get run with self.runGet...

        will not mark if state in skipIfIn

        """
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
                if service.getAction(action) == None:
                    continue
                service.state.set(action, state)
                service.state.save()

    def servicesFind(self, instance="", parent=None, first=False, role="", hasAction="", include_disabled=False, templatename=""):
        res = []

        for key, service in self.services.items():
            # if service._state and service._state.hrd.getBool('disabled', False) and not include_disabled:
            #     continue
            if not(instance == "" or service.instance == instance):
                continue
            if not(parent is None or service.parent == parent):
                continue
            if not(templatename is "" or service.templatename == templatename):
                continue
            if not(role == "" or role == service.role):
                continue
            if hasAction != "" and service.getAction(hasAction) == None:
                continue
            # if not(node is None or service.isOnNode(node)):
            #     continue
            res.append(service)
        if first:
            if len(res) == 0:
                raise j.exceptions.Input("cannot find service %s|%s:%s (%s)" % (
                    domain, service.templatename, instance, version), "ays.servicesFind")
            return res[0]
        return res

    def serviceFindProducer(self, producercategory, instancename):
        for item in self.servicesFind(instance=instancename):
            if producercategory in item.categories:
                return item

    def serviceFindConsumers(self, target):
        """
        @return set of services that consumes target
        """
        result = set()
        for service in self.servicesFind():
            if target.isConsumedBy(service):
                result.add(service)
        return result

    def serviceFindConsumersRecursive(self, target, out=set()):
        """
        @return set of services that consumes target, recursivlely
        """
        for service in self.findConsumers(target):
            out.add(service)
            self.findConsumersRecursive(service, out)
        return out

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

    def runFindActionScope(self, action, role="", instance="", producerRoles="*"):
        """
        find all services from role & instance and their producers
        only find producers wich have at least one of the actions
        """
        # create a scope in which we need to find work
        producerRoles = self._processProducerRoles(producerRoles)
        scope = set(self.servicesFind(
            role=role, instance=instance, hasAction=action))
        for service in scope:
            producer_candidates = service.getProducersRecursive(
                producers=set(), callers=set(), action=action, producerRoles=producerRoles)
            if producerRoles != '*':
                producer_valid = [
                    item for item in producer_candidates if item.role in producerRoles]
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
                producerroles = [item for item in producerroles.split(
                    ",") if item.strip() != ""]
            else:
                producerroles = [producerroles.strip()]
        return producerroles

    @property
    def runs(self):
        from IPython import embed
        print("DEBUG NOW do")
        embed()

        runs = AYSRun(self).list()
        return runs

    # def getSource(self, hash):
    #     raise j.exceptions.RuntimeError("should not be like thios")
    #     return AYSRun(self).getFile('source', hash)

    # def getHRD(self, hash):
    #     raise j.exceptions.RuntimeError("should not be like thios")
    #     return AYSRun(self).getFile('hrd', hash)

    def runGet(self, role="", instance="", action="install", force=False, producerRoles="*", data=None, id=0, simulate=False):
        """
        get a new run
        if id !=0 then the run will be loaded from DB
        """
        self._doinit()

        if id != 0:
            run = AYSRun(self, id=id)
            return run

        producerRoles = self._processProducerRoles(producerRoles)

        if action not in ["init"]:
            for key, s in self.services.items():
                if s.state.get("init") not in ["OK", "DO"]:
                    error_msg = "Cannot get run: %s:%s:%s because found a service not properly inited yet.\n%s\n please rerun ays init" % (
                        role, instance, action, s)
                    self.logger.error(error_msg)
                    raise j.exceptions.Input(error_msg, msgpub=error_msg)
        if force:
            self.setState(actions=[action], role=role,
                          instance=instance, state="DO")

        if action == "init":
            actions = ["init"]
        else:
            actions = ["install", action]

        run = AYSRun(self, simulate=simulate)
        for action0 in actions:
            scope = self.runFindActionScope(
                action=action0, role=role, instance=instance, producerRoles=producerRoles)
            todo = self._findTodo(
                action=action0, scope=scope, run=run, producerRoles=producerRoles)
            while todo != []:
                newstep = True
                for service in todo:
                    if service.state.get(action0, die=False) != "OK":
                        print("DO:%s %s" % (action, service))
                        if newstep:
                            step = run.newStep(action=action0)
                            newstep = False
                        step.addService(service)
                    if service in scope:
                        scope.remove(service)
                todo = self._findTodo(
                    action0, scope=scope, run=run, producerRoles=producerRoles)

        # these are destructive actions, they need to happens in reverse order
        # in the dependency tree
        if action in ['uninstall', 'removedata', 'cleanup', 'halt', 'stop']:
            run.reverse()

        return run

    def _findTodo(self, action, scope, run, producerRoles):
        if action == "" or action is None:
            raise RuntimeError("action cannot be empty")
        if scope == []:
            return []
        todo = list()
        waiting = False
        for service in scope:
            if run.exists(service, action):
                continue
            producersWaiting = service.getProducersRecursive(
                producers=set(), callers=set(), action=action, producerRoles=producerRoles)
            # remove the ones which are already in previous runs
            producersWaiting = [
                item for item in producersWaiting if run.exists(item, action) == False]
            producersWaiting = [item for item in producersWaiting if item.state.get(
                action, die=False) != "OK"]

            if len(producersWaiting) == 0:
                todo.append(service)
            elif j.application.debug:
                waiting = True

        if todo == [] and waiting:
            raise RuntimeError(
                "cannot find todo's for action:%s in scope:%s.\n\nDEPENDENCY ERROR: could not resolve dependency chain." % (action, scope))
        return todo

    def _getChangedServices(self, action=None):
        changed = list()
        if not action:
            actions = ["install", "stop", "start", "monitor", "halt", "check_up", "check_down",
                       "check_requirements", "cleanup", "data_export", "data_import", "uninstall", "removedata"]
        else:
            actions = [action]
        for _, service in self.services.items():
            if [service for action in actions if action in list(service.action_methods.keys()) and service.state.get(action, die=False) == 'CHANGED']:
                changed.append(service)
                for producers in [producers for _, producers in service.producers.items()]:
                    changed.extend(producers)
        return changed

# ACTIONS

    def init(self, role="", instance="", hasAction="", include_disabled=False, data=""):
        self._doinit()
        if role == "" and instance == "":
            self.reset()

        self.serviceSetState(actions=["init"], role=role,
                             instance=instance, state="INIT")
        for key, actor in self.actors.items():
            if role != "" and actor.role == role:
                continue
            actor.init()
            for inst in actor.listInstances():
                service = actor.aysrepo.getService(role=actor.role, instance=inst, die=False)
                print("RESETTING SERVICE roles %s inst %s instance %s " % (actor.role, inst, instance))
                service.update_hrd()

            #actor.newInstance(instance=key, args={})

        run = self.runGet(role=role, instance=instance,
                          data=data, action="init")
        run.execute()

        print("init done")

    def commit(self, message="", branch="master", push=True):
        self._doinit()
        if message == "":
            message = "log changes for repo:%s" % self.name
        if branch != "master":
            self.git.switchBranch(branch)

        self.git.commit(message, True)

        if push:
            print("PUSH")
            self.git.push()

    def update(self, branch="master"):
        j.atyourservice.updateTemplates()
        if branch != "master":
            self.git.switchBranch(branch)
        self.git.pull()

    def install(self, role="", instance="", force=True, producerRoles="*"):
        self._doinit()
        if force:
            self.setState(actions=["install"], role=role,
                          instance=instance, state='DO')

        run = self.runGet(action="install", force=force)
        print("RUN:INSTALL")
        print(run)
        run.execute()

    def uninstall(self, role="", instance="", force=True, producerRoles="*", printonly=False):
        self._doinit()
        if force:
            self.setState(actions=["stop", "uninstall"],
                          role=role, instance=instance, state='DO')

        run = self.runGet(action="stop", force=force)
        print("RUN:STOP")
        print(run)
        if not printonly:
            run.execute()

        run = self.runGet(role=role, instance=instance,
                          action="uninstall", force=force)
        print("RUN:UNINSTALL")
        print(run)
        if not printonly:
            run.execute()
        run.execute()
