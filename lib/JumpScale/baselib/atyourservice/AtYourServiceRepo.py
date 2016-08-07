from JumpScale import j

from JumpScale.baselib.atyourservice.ServiceRecipe import ServiceRecipe
from JumpScale.baselib.atyourservice.Service import Service, loadmodule
from JumpScale.baselib.atyourservice.ActionsBaseNode import ActionsBaseNode
from JumpScale.baselib.atyourservice.ActionsBaseMgmt import ActionsBaseMgmt
from JumpScale.baselib.atyourservice.ServiceTemplate import ServiceTemplate
from JumpScale.baselib.atyourservice.ActionMethodDecorator import ActionMethodDecorator
from JumpScale.baselib.atyourservice.Blueprint import Blueprint
from JumpScale.baselib.atyourservice.AYSRun import AYSRun
# from AYSdb import *

import colored_traceback
colored_traceback.add_hook(always=True)


class AtYourServiceRepo():

    def __init__(self, name, path="",keephistory=True):
        self._init = False

        # self._justinstalled = []
        self._type = None

        self._services = {}
        self._recipes = {}

        self._templates = {}

        self.indocker = j.atyourservice.indocker
        self.debug = j.atyourservice.debug
        self.logger = j.atyourservice.logger

        self._todo = []

        self.name = name
        self._basepath = path
        self._git = None

        self._blueprints = {}

        # self._roletemplates = dict()
        self._servicesTree = {}
        # self._db=AYSDB()
        self._load_blueprints()
        self.keephistory=keephistory
        if self.keephistory:
            self.db = j.servers.kvs.getFSStore("ays_%s"%self.name)
        else:
            self.db=None


    def _doinit(self):
        j.actions.setRunId("ays_%s" % self.name)

    def reset(self):
        # self._db.reload()
        j.dirs._ays = None
        self._services = {}
        self._recipes = {}
        self._templates = {}
        # self._reposDone = {}
        self._todo = []
        self._git = None
        self._blueprints = {}
        self._load_blueprints()
        self._servicesTree = {}

    def destroy(self, uninstall=True):
        if uninstall:
            self.uninstall()
        j.sal.fs.removeDirTree(j.sal.fs.joinPaths(self.basepath, "recipes"))
        j.sal.fs.removeDirTree(j.sal.fs.joinPaths(self.basepath, "services"))
        self.db.destroy()

    @property
    def basepath(self):
        if self._basepath is None or self._basepath == "":
            self.basepath = j.sal.fs.getcwd()
        return self._basepath

    @basepath.setter
    def basepath(self, val):
        self.reset()
        baseDir = val
        if not j.sal.fs.exists(path=baseDir):
            raise j.exceptions.Input("Can not find based dir for ays in %s" % baseDir)

        while j.sal.fs.joinPaths(baseDir, ".ays") not in j.sal.fs.listFilesInDir(baseDir, recursive=False):
            baseDir = j.sal.fs.getParent(baseDir)
            baseDir = baseDir.rstrip("/")

            if baseDir.strip() == "":
                if 'darwin' in j.core.platformtype.myplatform.platformtypes:
                    baseDir = "%s/ays/" % j.dirs.cfgDir
                else:
                    baseDir = "/etc/ays/local"
                break

        if baseDir.strip("/").strip() == "":
            raise j.exceptions.Input("Can not find based dir for ays in %s, after looking for parents." % val)

        self._basepath = baseDir
        for item in ["blueprints", "recipes", "services", "servicetemplates"]:
            # make sure basic dirs exist
            j.sal.fs.createDir(j.sal.fs.joinPaths(self._basepath, item))

    @property
    def git(self):
        if self._git is None:
            self._git = j.clients.git.get(basedir=self.basepath)
        return self._git

    # @property
    # def type(self):
    #     if self._type is not None:
    #         return self._type
    #     self._type = "n"  # n from normal
    #     # check if we are in a git directory, if so we will use $thatdir/services as base for the metadata
    #     if self.basepath is not None:
    #         self._type = "c"
    #     return self._type

    @property
    def templates(self):
        self._doinit()
        if self._templates == {}:
            # need to link to templates of factory and then overrule with the local ones
            for key, template in j.atyourservice.templates.items():
                self._templates[key] = template

        def load(domain, path):
            for servicepath in j.sal.fs.listDirsInDir(path, recursive=False):
                dirname = j.sal.fs.getBaseName(servicepath)
                # print "dirname:%s"%dirname
                if not (dirname.startswith(".")):
                    load(domain, servicepath)
            # print path
            dirname = j.sal.fs.getBaseName(path)
            if dirname.startswith("_"):
                return
            tocheck = ['schema.hrd', 'service.hrd', 'actions_mgmt.py', 'actions_node.py', 'model.py', 'actions.py']
            exists = [True for aysfile in tocheck if j.sal.fs.exists('%s/%s' % (path, aysfile))]
            if exists:
                templ = ServiceTemplate(path, domain=domain)
                self._templates[templ.name] = templ  # overrule the factory ones with the local ones

        # load local templates
        path = j.sal.fs.joinPaths(self.basepath, "servicetemplates/")
        if j.sal.fs.exists(path):
            load(self.name, path)

        return self._templates

    @property
    def recipes(self):
        self._doinit()
        if not self._recipes:
            aysrepopath = self.basepath
            if aysrepopath is not None:
                # load local templates
                domainpath = j.sal.fs.joinPaths(aysrepopath, "recipes")
                if not j.sal.fs.exists(domainpath):
                    return {}
                d = j.tools.path.get(domainpath)
                for item in d.walkfiles("state.json"):
                    recipepath = j.sal.fs.getDirName(item)
                    recipe = ServiceRecipe(self, recipepath)
                    if recipe.name in self._recipes:
                        raise j.exceptions.Input("Found double recipe: %s" % recipe)
                    self._recipes[recipe.name] = recipe
        return self._recipes

    @property
    def services(self):
        self._doinit()
        if self._services == {}:
            services_path = j.sal.fs.joinPaths(self.basepath, "services")
            if not j.sal.fs.exists(services_path):
                return {}
            for hrd_path in j.sal.fs.listFilesInDir(services_path, recursive=True, filter="state.yaml",
                                                    case_sensitivity='os', followSymlinks=True, listSymlinks=False):
                service_path = j.sal.fs.getDirName(hrd_path)
                service = Service(self, path=service_path, args=None)
                self._services[service.key] = service
        return self._services

    # def _nodechildren(self, service, parent=None, producers=[]):
    #     parent = {} if parent is None else parent
    #     me = {"name": service.key, "children": []}
    #     parent["children"].append(me)
    #     details = service.hrd.getHRDAsDict()
    #     details = {key: value for key, value in details.items() if key not in ['service.domain', 'service.name', 'service.version', 'parent']}
    #     me["data"] = details
    #     children = service.listChildren()
    #     for role, instances in children.items():
    #         for instance in instances:
    #             child = j.atyourservice.getService(role=role, instance=instance)
    #             for _, producerinstances in child.producers.items():
    #                 for producer in producerinstances:
    #                     producers.append([child.key, producer.key])
    #             self._nodechildren(child, me, producers)
    #     return parent

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
            parents["children"].append(self._nodechildren(service, {"children": [], "name": servicekey}, producers))
        self._servicesTree['parentchild'] = parents
        self._servicesTree['producerconsumer'] = producers
        return self._servicesTree

    def _load_blueprints(self):
        bpdir=j.sal.fs.joinPaths(self.basepath, "blueprints")
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
    def blueprints_disabled(self):
        """
        Show the disabled blueprints
        """
        bps = []
        for path,bp in self._blueprints.items():
            if bp.active==False:
                bps.append(bp)
        bps = sorted(bps, key=lambda bp: bp.name)
        return bps

    def archive_blueprint(self, bp):
        raise RuntimeError("no longer supported, use bp.disable()")

    def restore_blueprint(self, bp):
        raise RuntimeError("no longer supported, use bp.enable()")

    def execute_blueprint(self, path="", content="", role="", instance=""):
        self._doinit()
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

    def init(self, role="", instance="", hasAction="", include_disabled=False, data=""):
        self._doinit()
        if role == "" and instance == "":
            self.reset()

        self.setState(actions=["init"], role=role, instance=instance, state="INIT")
        for key, recipe in self.recipes.items():
            if role != "" and recipe.role == role:
                continue
            recipe.init()
            for inst in recipe.listInstances():
                service = recipe.aysrepo.getService(role=recipe.role, instance=inst, die=False)
                print("RESETTING SERVICE roles %s inst %s instance %s "%(recipe.role, inst, instance))
                service.update_hrd()

            #import pudb; pu.db
            #recipe.newInstance(instance=key, args={})

        run = self.getRun(role=role, instance=instance, data=data, action="init")
        run.execute()

        print("init done")

    def getBlueprint(self, path):
        self._doinit()
        for bp in self.blueprints:
            if bp.path == path:
                return bp
        return Blueprint(self, path)

    # def getRoleTemplateClass(self, role, ttype):
    #     if role not in self.roletemplates:
    #         raise j.exceptions.RuntimeError('Role template %s does not exist' % role)
    #     roletemplatepaths = self.roletemplates[role]
    #     for roletemplatepath in roletemplatepaths:
    #         if ttype in j.sal.fs.getBaseName(roletemplatepath):
    #             modulename = "JumpScale.atyourservice.roletemplate.%s.%s" % (role, ttype)
    #             mod = loadmodule(modulename, roletemplatepath)
    #             return mod.Actions
    #     return None

    # def getRoleTemplateHRD(self, role):
    #     if role not in self.roletemplates:
    #         raise j.exceptions.RuntimeError('Role template %s does not exist' % role)
    #     roletemplatepaths = self.roletemplates[role]
    #     hrdpaths = [path for path in roletemplatepaths if j.sal.fs.getFileExtension(path) == 'hrd']
    #     if hrdpaths:
    #         hrd = j.data.hrd.getSchema(hrdpaths[0])
    #         for path in hrdpaths[1:]:
    #             hrdtemp = j.data.hrd.getSchema(path)
    #             hrd.items.update(hrdtemp.items)
    #         return hrd.hrdGet()
    #     return None

    def setState(self, actions=[], role="", instance="", state="DO"):
        """
        get run with self.getRun...

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

    def findActionScope(self, action, role="", instance="", producerRoles="*"):
        """
        find all services from role & instance and their producers
        only find producers wich have at least one of the actions
        """
        # create a scope in which we need to find work
        producerRoles = self._processProducerRoles(producerRoles)
        scope = set(self.findServices(role=role, instance=instance, hasAction=action))
        for service in scope:
            producer_candidates = service.getProducersRecursive(producers=set(), callers=set(), action=action, producerRoles=producerRoles)
            if producerRoles != '*':
                producer_valid = [item for item in producer_candidates if item.role in producerRoles]
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

    def listRuns(self):
        runs = AYSRun(self).list()
        return runs

    def getSource(self, hash):
        return AYSRun(self).getFile('source', hash)

    def getHRD(self, hash):
        return AYSRun(self).getFile('hrd', hash)

    def getRun(self, role="", instance="", action="install", force=False, producerRoles="*", data=None, id=0, simulate=False):
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
                    error_msg = "Cannot get run: %s:%s:%s because found a service not properly inited yet.\n%s\n please rerun ays init" % (role, instance, action, s)
                    self.logger.error(error_msg)
                    raise j.exceptions.Input(error_msg, msgpub=error_msg)
        if force:
            self.setState(actions=[action], role=role, instance=instance, state="DO")

        if action == "init":
            actions = ["init"]
        else:
            actions = ["install", action]

        run = AYSRun(self, simulate=simulate)
        for action0 in actions:
            scope = self.findActionScope(action=action0, role=role, instance=instance, producerRoles=producerRoles)
            todo = self._findTodo(action=action0, scope=scope, run=run, producerRoles=producerRoles)
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
                todo = self._findTodo(action0, scope=scope, run=run, producerRoles=producerRoles)

        # these are destructive actions, they need to happens in reverse order in the dependency tree
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
            producersWaiting = service.getProducersRecursive(producers=set(), callers=set(), action=action, producerRoles=producerRoles)
            # remove the ones which are already in previous runs
            producersWaiting = [item for item in producersWaiting if run.exists(item, action) == False]
            producersWaiting = [item for item in producersWaiting if item.state.get(action, die=False) != "OK"]

            if len(producersWaiting) == 0:
                todo.append(service)
            elif j.application.debug:
                waiting = True

        if todo == [] and waiting:
            raise RuntimeError("cannot find todo's for action:%s in scope:%s.\n\nDEPENDENCY ERROR: could not resolve dependency chain." % (action, scope))
        return todo

    def commit(self, message="", branch="master", push=True):
        self._doinit()
        if message == "":
            message = "log changes for repo:%s" % self.name
        gitcl = j.clients.git.get(self.basepath)
        if branch != "master":
            gitcl.switchBranch(branch)

        gitcl.commit(message, True)

        if push:
            print("PUSH")
            gitcl.push()

    def update(self, branch="master"):
        j.atyourservice.updateTemplates()
        gitcl = j.clients.git.get(self.basepath)
        if branch != "master":
            gitcl.switchBranch(branch)
        gitcl.pull()

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

    def install(self, role="", instance="", force=True, producerRoles="*"):
        self._doinit()
        if force:
            self.setState(actions=["install"], role=role, instance=instance, state='DO')

        run = self.getRun(action="install", force=force)
        print("RUN:INSTALL")
        print(run)
        run.execute()

    def uninstall(self, role="", instance="", force=True, producerRoles="*", printonly=False):
        self._doinit()
        if force:
            self.setState(actions=["stop", "uninstall"], role=role, instance=instance, state='DO')

        run = self.getRun(action="stop", force=force)
        print("RUN:STOP")
        print(run)
        if not printonly:
            run.execute()

        run = self.getRun(role=role, instance=instance, action="uninstall", force=force)
        print("RUN:UNINSTALL")
        print(run)
        if not printonly:
            run.execute()
        run.execute()

    def findRecipes(self, name="", version="", role=''):
        res = []
        domain = "ays"
        for template in self.recipes:
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

    def findServices(self, instance="", parent=None, first=False, role="", hasAction="", include_disabled=False, templatename=""):
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
                raise j.exceptions.Input("cannot find service %s|%s:%s (%s)" % (domain, name, instance, version), "ays.findServices")
            return res[0]
        return res

    def findProducer(self, producercategory, instancename):
        for item in self.findServices(instance=instancename):
            if producercategory in item.categories:
                return item

    def findConsumers(self, target):
        """
        @return set of services that consumes target
        """
        result = set()
        for service in self.findServices():
            if target.isConsumedBy(service):
                result.add(service)
        return result

    def findConsumersRecursive(self, target, out=set()):
        """
        @return set of services that consumes target, recursivlely
        """
        for service in self.findConsumers(target):
            out.add(service)
            self.findConsumersRecursive(service, out)
        return out

    def new(self, name="", instance="main", path=None, parent=None, args={}, consume="", model=None):
        """
        will create a new service from template

        @param args are the arguments which will overrule questions of the instance.hrd
        @param consume specifies which ays instances will be consumed
                format $role/$domain|$name!$instance,$role2/$domain2|$name2!$instance2

        """
        self._doinit()
        recipe = self.getRecipe(name)
        obj = recipe.newInstance(instance=instance, path=path, parent=parent, args=args, consume=consume, model=model)
        return obj

    def remove(self, name="", instance="", domain="", role=""):
        for service in self.findServices(domain=domain, name=name, instance=instance, role=role):
            if service in self.services:
                self.services.remove(service)
            j.sal.fs.removeDirTree(service.path)

    def getTemplate(self, name, die=True):
        """
        @param first means, will only return first found template instance
        """
        if name in self.templates:
            return self.templates[name]
        if die:
            raise j.exceptions.Input("Cannot find template with name:%s" % name)

    def existsTemplate(self, name):
        if self.getTemplate(name, die=False) == None:
            return False
        return True

    def existsRecipe(self, name):
        if self.getRecipe(name, die=False) == None:
            return False
        return True

    def getRecipe(self, name, die=True):
        if name in self.recipes:
            recipe = self.recipes[name]
            return recipe
        else:
            template = self.getTemplate(name=name, die=die)
            if die == False and template == None:
                return None
            recipe = template.getRecipe(self)
            self._recipes[recipe.name] = recipe
            return recipe
        if die:
            raise j.exceptions.Input("Cannot find recipe with name:%s" % name)

    def getService(self, role, instance, die=True):
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

    def getServiceFromKey(self, key):
        """
        key in format $reponame!$name!$instance@role ($version)

        """
        if key.count("!") == 2:
            reponame, role, instance = key.split("!")
        else:
            role, instance = key.split("!")
        return self.getService(instance=instance, role=role, die=True)
