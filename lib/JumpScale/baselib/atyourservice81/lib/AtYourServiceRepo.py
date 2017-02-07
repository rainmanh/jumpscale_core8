from JumpScale import j
from JumpScale.baselib.atyourservice81.lib.Actor import Actor
from JumpScale.baselib.atyourservice81.lib.Service import Service
from JumpScale.baselib.atyourservice81.lib.Blueprint import Blueprint
from JumpScale.baselib.atyourservice81.lib.models.ActorsCollection import ActorsCollection
from JumpScale.baselib.atyourservice81.lib.models.ServicesCollection import ServicesCollection
from JumpScale.baselib.atyourservice81.lib.AtYourServiceDependencies import build_nodes, create_graphs, get_task_batches, create_job
import asyncio

import colored_traceback
colored_traceback.add_hook(always=True)
from collections import namedtuple



class AtYourServiceRepoCollection:

    def __init__(self):
        self.logger = j.logger.get('j.atyourservice')
        self._loop = asyncio.get_event_loop()
        self._repos = {}
        self._loop.call_soon(self._load)

    def _load(self):
        self.logger.info("reload AYS repos")
        # search repo on the filesystem
        for dir_path in [j.dirs.CODEDIR, j.dirs.VARDIR]:
            for path in self._searchAysRepos(dir_path):
                if path not in self._repos:
                    self.logger.info("AYS repo found {}".format(path))
                    repo = AtYourServiceRepo(path)
                    self._repos[repo.path] = repo

        # make sure all loaded repo still exists
        for repo in list(self._repos.values()):
            if not j.sal.fs.exists(repo.path):
                self.logger.info("repo {} doesnt exists anymore, unload".format(repo.path))
                del(self._repos[repo.path])

        self._loop.call_later(60, self._load)

    def _searchAysRepos(self, path):
        """
        walk over path recursively to look for AYS repository
        return path to AYS repository found
        """
        path = j.sal.fs.pathNormalize(path)

        res = []

        def callbackFunctionDir(path, arg):
            if j.sal.fs.exists("%s/.ays" % path):
                arg[1].append(path)

        def callbackForMatchDir(path, arg):
            base = j.sal.fs.getBaseName(path)
            if base in [".git", ".hg", ".github"]:
                return False
            depth = len(j.sal.fs.pathRemoveDirPart(path, arg[0]).split("/"))
            # print("%s:%s" % (depth, j.sal.fs.pathRemoveDirPart(path, arg[0])))
            if depth < 6:
                return True
            return False

        j.sal.fswalker.walkFunctional(path, callbackFunctionFile=None, callbackFunctionDir=callbackFunctionDir, arg=[path, res],
                                      callbackForMatchDir=callbackForMatchDir, callbackForMatchFile=lambda x,y: False)
        return res

    def list(self):
        # TODO protect by lock and auto update
        return list(self._repos.values())

    def create(self, path, git_url=''):
        path = j.sal.fs.pathNormalize(path)

        if j.sal.fs.exists(path):
            raise j.exceptions.Input("Directory %s already exists. Can't create AYS repo at the same location." % path)

        j.sal.fs.createDir(path)
        j.sal.fs.createEmptyFile(j.sal.fs.joinPaths(path, '.ays'))
        j.sal.fs.createDir(j.sal.fs.joinPaths(path, 'actorTemplates'))
        j.sal.fs.createDir(j.sal.fs.joinPaths(path, 'blueprints'))
        j.tools.cuisine.local.core.run('cd {};git init'.format(path))
        if git_url:
            j.tools.cuisine.local.core.run('cd {path};git remote add origin {url}'.format(path=path, url=git_url))
        j.sal.nettools.download(
            'https://raw.githubusercontent.com/github/gitignore/master/Python.gitignore', j.sal.fs.joinPaths(path, '.gitignore'))
        name = j.sal.fs.getBaseName(path)
        # TODO lock
        self._repos[path] = AtYourServiceRepo(path=path)
        print("AYS Repo created at %s" % path)
        return self._repos[path]

    def get(self, path=None):
        """
        @param path: path of the AYS Repo, if None use current working directory
        @return:    @AtYourServiceRepo object
        """
        if path is None:
            path = j.sal.fs.getcwd()

        for repo in self._repos.values():
            if j.sal.fs.pathClean(repo.path) == j.sal.fs.pathClean(path):
                return repo

        raise j.exceptions.NotFound(message="Could not find repo in path:%s" %
                                     path, level=1, source="", tags="", msgpub="")

    def delete(self, repo):
        if repo.path in self._repos:
            del(self._repos[repo.path])

VALID_ACTION_STATE = ['new', 'installing', 'ok', 'error', 'disabled', 'changed']

DBTuple = namedtuple("DB", ['actors', 'services'])

class AtYourServiceRepo():

    def __init__(self, path, model=None):
        self.logger = j.logger.get('j.atyourservice')
        self.path = j.sal.fs.pathNormalize(path)
        self.name = j.sal.fs.getBaseName(self.path)
        self.git = j.clients.git.get(self.path, check_path=False)
        self._db = None
        self.no_exec = False
        j.atyourservice._loadActionBase()

        self._services = {}
        self._load_services()

    @property
    def db(self):
        if self._db is None:
            self._db = DBTuple(
                ActorsCollection(self),
                ServicesCollection(self)
            )
        return self._db

    def _load_services(self):
        """
        load the services from the filesystem when AYS starts
        """
        services_dir = j.sal.fs.joinPaths(self.path, 'services')
        if j.sal.fs.exists(services_dir) and len(self.services) <= 0:
            for service_path in j.sal.fs.listDirsInDir(services_dir, recursive=True):
                s = Service.init_from_fs(aysrepo=self, path=service_path)
                self._services[s.model.key] = s

    def destroy(self):
        self.db.actors.destroy()
        self.db.services.destroy()
        for run in self.runsList():
            run.delete()
        j.sal.fs.removeDirTree(j.sal.fs.joinPaths(self.path, "actors"))
        j.sal.fs.removeDirTree(j.sal.fs.joinPaths(self.path, "services"))
        j.sal.fs.removeDirTree(j.sal.fs.joinPaths(self.path, "recipes"))  # for old time sake
        j.atyourservice.aysRepos.delete(self)

    def enable_noexec(self):
        """
        Enable the no_exec mode.
        Once this mode is enabled, no action will ever be execute.
        But the state of the action will be updated as if everything went fine (state ok)

        This mode can be used for demo or testing
        """
        # self.model.enable_no_exec()
        self.no_exec = True

    def disable_noexec(self):
        """
        Enable the no_exec mode.

        see enable_no_exec for further info
        """
        self.no_exec = False
        # self.model.disable_no_exec()

# ACTORS
    def actorCreate(self, name):
        """
        will look for name inside & create actor from it
        """
        actorTemplate = self.templateGet(name)
        actor = Actor(aysrepo=self, template=actorTemplate)
        return actor

    def actorGet(self, name, die=False):
        actor_models = self.db.actors.find(name=name)
        if len(actor_models) == 1:
            obj = actor_models[0].objectGet(self)
        elif len(actor_models) > 1:
            raise j.exceptions.Input(message="More than one actor found with name:%s" %
                                     name, level=1, source="", tags="", msgpub="")
        elif len(actor_models) < 1:
            # checking if we have the actor on the file system
            actors_dir = j.sal.fs.joinPaths(self.path, 'actors')
            results = j.sal.fs.walkExtended(actors_dir, files=False, dirPattern=name)
            if len(results) == 1:
                return Actor(aysrepo=self, name=name)
            elif die:
                raise j.exceptions.NotFound(message="Could not find actor with name:%s" %
                                         name, level=1, source="", tags="", msgpub="")

            obj = self.actorCreate(name)

        return obj

    def actorGetByKey(self, key):
        return self.db.actors.get(key).objectGet(self)

    def actorExists(self, name):
        len(self.db.actors.find(name=name)) > 0

    @property
    def actors(self):
        actors = {}
        for model in self.db.actors.find():
            if model.dbobj.state != "disabled":
                actors[model.dbobj.name] = model.objectGet(aysrepo=self)
        return actors

# TEMPLATES

    @property
    def templates(self):
        templates = {}
        # need to link to templates of factory and then overrule with the local ones
        for template in j.atyourservice.actorTemplates:
            templates[template.name] = template

        # load local templates
        templateRepo = j.atyourservice.templateRepos.create(self.path)
        for template in templateRepo.templates:
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

    @property
    def services(self):
        services = []
        for service in self._services.values():
            if service.model.dbobj.state != "disabled":
                services.append(service)
        return services

    def serviceGet(self, role, instance, key=None, die=True):
        """
        Return service indentifier by role and instance or key
        throw error if service is not found or if more than one service is found
        """
        if role.strip() == "" or instance.strip() == "":
            raise j.exceptions.Input("role and instance cannot be empty.")

        # objs = self.db.services.find(actor="%s.*" % role, name=instance)
        objs = [s for s in self._services.values() if s.model.role == role and s.name == instance]
        if len(objs) == 0:
            if die:
                raise j.exceptions.NotFound(message="Cannot find service %s:%s" %
                                         (role, instance), level=1, source="", tags="", msgpub="")
            return None
        # return objs[0].objectGet(self)
        return objs[0]

    def serviceGetByKey(self, key):
        objs = [s for s in self._services.values() if s.model.key == key]
        if len(objs) <= 0:
            raise j.exceptions.NotFound(message="Cannot find service with key {}".format(key))
        return objs[0]
        # return self.db.services.get(key=key).objectGet(self)

    @property
    def serviceKeys(self):
        return [s.model.key for s in self._services.values()]
        # return [model.key for model in self.db.services.find()]

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

    def servicesFind(self, name="", actor="", role="", state="", parent="", producer="", hasAction="",
                     includeDisabled=False, first=False):
        """
        @param name can be the full name e.g. myappserver or a prefix but then use e.g. myapp.*
        @param actor can be the full name e.g. node.ssh or role e.g. node.*
                            (but then need to use the .* extension, which will match roles)
                            exclusive with role argument
        @param role role of the service. exclusive with actor argument
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
        results = []
        for service in self._services.values():
            if name != '' and service.name != name:
                continue

            if actor != '' and service.model.dbobj.actorName != actor:
                continue

            if role != '' and service.model.role != role:
                continue

            if state != '' and service.model.state != state:
                continue

            if parent != '' and "{}!{}".format(service.parent.role, service.parent.name) != parent:
                continue

            # if producer != '':
            #     for prod in service.producers:
            #         if "{}!{}".format(prod.role, prod.name) !=

            if includeDisabled is False and service.model.dbobj.state == "disabled":
                continue

            if hasAction != "" and hasAction not in service.model.actions.keys():
                continue

            results.append(service)

        if first:
            if len(results) == 0:
                raise j.exceptions.NotFound("cannot find service %s|%s:%s" % (self.name, actor, name), "ays.servicesFind")
            return results[0]
        return results

        # if actor == '' and role != '':
        #     actor = '%s(\..*)?' % role
        #
        # res = []
        # for service_model in self.db.services.find(name=name, actor=actor, state=state, parent=parent, producer=producer):
        #     if hasAction != "" and hasAction not in service_model.actionsState.keys():
        #         continue
        #
        #     if includeDisabled is False and service_model.dbobj.state == "disabled":
        #         continue

        #     res.append(service_model.objectGet(self))
        # if first:
        #     if len(res) == 0:
        #         raise j.exceptions.Input("cannot find service %s|%s:%s" % (self.name, actor, name), "ays.servicesFind")
        #     return res[0]
        # return res

# BLUEPRINTS

    def get_blueprints_paths(self):
        bpdir = j.sal.fs.joinPaths(self.path, "blueprints")
        items = []
        if j.sal.fs.exists(path=bpdir):
            items = j.sal.fs.listFilesInDir(bpdir)
            return items

    def _load_blueprints(self):
        bps = {}
        items = self.get_blueprints_paths()
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
        for path, bp in self._load_blueprints().items():
            if bp.active is False:
                bps.append(bp)
        bps = sorted(bps, key=lambda bp: bp.name)
        return bps

    async def blueprintExecute(self, path="", content="", role="", instance=""):
        if path == "" and content == "":
            for bp in self.blueprints:
                if not bp.is_valid:
                    self.logger.warning("blueprint %s not executed because it doesn't have a valid format" % bp.path)
                    return
                await bp.load(role=role, instance=instance)
        else:
            bp = Blueprint(self, path=path, content=content)
            # self._blueprints[bp.path] = bp
            if not bp.is_valid:
                return
            await bp.load(role=role, instance=instance)

        await self.init(role=role, instance=instance)

        print("blueprint done")

    def blueprintGet(self, bname):
        bpath = j.sal.fs.joinPaths(self.path, 'blueprints', bname)

        for bp in self.blueprints:
            if bp.path == bpath:
                return bp
        return Blueprint(self, bpath)

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

    def runGet(self, runkey):
        """
        Get Run by id
        """
        if j.core.jobcontroller.db.runs.exists(runkey):
            return j.core.jobcontroller.db.runs.get(runkey)
        raise j.exceptions.NotFound('No run with key %s found' % runkey)

    def runsList(self):
        """
        list Runs on repo
        """
        runs_models = j.core.jobcontroller.db.runs.find(repo=self.path)


        return [run.objectGet() for run in runs_models]

    def findScheduledActions(self):
        """
        Walk over all servies and look for action with state scheduled.
        It then creates actions chains for all schedules actions.
        """
        result = {}
        for service in self.services:
            service_model = service.model
            for action, state in service_model.actionsState.items():
                if state in ['scheduled', 'changed', 'error']:
                    if service_model not in result:
                        result[service_model] = list()
                    action_chain = list()
                    service_model._build_actions_chain(action, ds=action_chain)
                    action_chain.reverse()
                    result[service_model].append(action_chain)
        return result

    def runCreate(self, debug=False, profile=False):
        """
        Create a run from all the scheduled actions in the repository.
        """
        all_nodes = build_nodes(self)
        nodes = create_graphs(self, all_nodes)
        run = j.core.jobcontroller.newRun(repo=self.path)

        for bundle in get_task_batches(nodes):
            to_add = []

            for node in bundle:
                if node.model.actionsState[node.action] != 'ok':
                    to_add.append(node)

            if len(to_add) > 0:
                step = run.newStep()

            for node in to_add:
                job = create_job(self, node.model, node.action)

                job.model.dbobj.profile = profile
                job.model.dbobj.debug = profile if profile is True else debug

                step.addJob(job)

        return run

# ACTIONS
    async def init(self, role="", instance="", hasAction="", includeDisabled=False, data=""):
        for service in self.servicesFind(name=instance, actor='%s.*' % role, hasAction=hasAction, includeDisabled=includeDisabled):
            self.logger.info('init service: %s' % service)
            await service.init()

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
