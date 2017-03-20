from JumpScale import j

from JumpScale.baselib.atyourservice81.Actor import Actor
from JumpScale.baselib.atyourservice81.Blueprint import Blueprint
from JumpScale.baselib.atyourservice81.models.ActorsCollection import ActorsCollection
from JumpScale.baselib.atyourservice81.models.ServicesCollection import  ServicesCollection
from JumpScale.baselib.jobcontroller.models.JobsCollections import JobsCollection
from JumpScale.baselib.atyourservice81.AtYourServiceDependencies import build_nodes, create_graphs, get_task_batches, create_job

import colored_traceback
colored_traceback.add_hook(always=True)
import yaml
import os
from collections import namedtuple

VALID_ACTION_STATE = ['new', 'installing', 'ok', 'error', 'disabled', 'changed']

DBTuple = namedtuple("DB", ['actors', 'services'])

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

        self._db = None
        if model is None:
            self.model = j.atyourservice._repos.find(path=path)[0]
        else:
            self.model = model

        j.atyourservice._loadActionBase()

    @property
    def db(self):
        if self._db is None:
            self._db = DBTuple(
                ActorsCollection(self),
                ServicesCollection(self)
            )
        return self._db


    def _getsshconnections(self, service_path):
        # get ssh connections from ays services path
        c = j.tools.cuisine.local
        if not j.sal.fs.exists(service_path):
            return
        if not j.sal.fs.exists("%s/.ssh/known_hosts" % j.dirs.homeDir):
            return
        _, out, _ = c.core.run("find %s -name 'data.json' -exec egrep -iH 'ippublic|sshPort' {} \;" % service_path,
                               showout=False)
        connections = dict()
        if out:
            for item in out.splitlines():
                # example line
                # "'./services/node!tweakernode/os!tweakernode/data.json: "sshPort":2203,'"
                results = item.replace('"', '').replace(',', '').split(':')
                if results[0] not in connections:
                    connections[results[0]] = dict()
                if results[1].strip() == 'sshPort' and 'port' not in connections[results[0]]:
                    connections[results[0]]['port'] = results[2]
                elif results[1].strip() == 'ipPublic'and 'ip' not in connections[results[0]]:
                    connections[results[0]]['ip'] = results[2]
        return connections

    def destroy(self):
        # remove ips from known hosts
        c = j.tools.cuisine.local
        service_path = j.sal.fs.joinPaths(self.path, "services")
        connections = self._getsshconnections(service_path)
        if connections:
            for key, val in connections.items():
                if 'ip' in val and val['ip'].strip():
                    if 'port' not in val:
                        c.core.run('ssh-keygen -f "%s/.ssh/known_hosts" -R %s' % (j.dirs.homeDir, val['ip']))
                    else:
                        c.core.run('ssh-keygen -f "%s/.ssh/known_hosts" -R \'[%s]:%s\'' % (j.dirs.homeDir, val['ip'],
                                                                                           val['port']))

        j.sal.fs.removeDirTree(service_path)
        j.sal.fs.removeDirTree(j.sal.fs.joinPaths(self.path, "actors"))
        j.sal.fs.removeDirTree(j.sal.fs.joinPaths(self.path, "recipes"))  # for old time sake

        # removing the related jobs
        jobs = set()
        services = self.db.services.list()
        jc = JobsCollection()
        for service in services:
            job_keys = jc._list_keys(serviceKey=service)
            for job_key in job_keys:
                index = jc.getIndexFromKey(job_key)
                if index:
                    jobs.add(index)
                else:
                    self.logger.warn('No index found job with key [%s]' % job_key)
        jc._db.index_remove(list(jobs))

        # removing related actors, services , and the repo model itslef.
        self.db.actors.destroy()
        self.db.services.destroy()
        self.model.delete()

    def enable_noexec(self):
        """
        Enable the no_exec mode.
        Once this mode is enabled, no action will ever be execute.
        But the state of the action will be updated as if everything went fine (state ok)

        This mode can be used for demo or testing
        """
        self.model.enable_no_exec()

    def disable_noexec(self):
        """
        Enable the no_exec mode.

        see enable_no_exec for further info
        """
        self.model.disable_no_exec()

# ACTORS
    def actorCreate(self, name):
        """
        will look for name inside & create actor from it
        """
        actorTemplate = self.templateGet(name)
        actor = Actor(aysrepo=self, template=actorTemplate)
        return actor

    def actorGet(self, name, reload=False, die=False):
        actor_models = self.db.actors.find(name=name)
        if len(actor_models) == 1:
            obj = actor_models[0].objectGet(self)
        elif len(actor_models) > 1:
            raise j.exceptions.Input(message="More than one actor found with name:%s" % name, level=1, source="", tags="", msgpub="")
        elif len(actor_models) < 1:
            # checking if we have the actor on the file system
            actors_dir = j.sal.fs.joinPaths(self.path, 'actors')
            results = j.sal.fs.walkExtended(actors_dir, files=False, dirPattern=name)
            if len(results) == 1:
                return Actor(aysrepo=self, name=name)
            elif die:
                raise j.exceptions.Input(message="Could not find actor with name:%s" % name, level=1, source="", tags="", msgpub="")

            obj = self.actorCreate(name)

        if reload:
            obj.loadFromFS()

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
        """
        """
        templates = {}
        # need to link to templates of factory and then overrule with the local ones
        for key, template in j.atyourservice.actorTemplates.items():
            templates[key] = template

        # load local templates
        path = j.sal.fs.joinPaths(self.path, "actorTemplates")
        if j.sal.fs.exists(path):
            for template in j.atyourservice._actorTemplatesGet(self.git, path=path, aysrepo=self, result=[]):
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
        for service_model in self.db.services.find():
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

        objs = self.db.services.find(actor="%s.*" % role, name=instance)
        if len(objs) == 0:
            if die:
                raise j.exceptions.Input(message="Cannot find service %s:%s" %
                                         (role, instance), level=1, source="", tags="", msgpub="")
            return None
        return objs[0].objectGet(self)

    def serviceGetByKey(self, key):
        return self.db.services.get(key=key).objectGet(self)

    @property
    def serviceKeys(self):
        return [model.key for model in self.db.services.find()]

    # @property
    # def servicesTree(self):
    #     # TODO: implement, needs to come from db now
    #     raise RuntimeError()

    #     if self._servicesTree:
    #         return self._servicesTree

    #     producers = []
    #     parents = {"name": "sudoroot", "children": []}
    #     for root in j.sal.fs.walk(j.dirs.ays, recurse=1, pattern='*state.yaml', return_files=1, depth=2):
    #         servicekey = j.sal.fs.getBaseName(j.sal.fs.getDirName(root))
    #         service = self.services.get(servicekey)
    #         for _, producerinstances in service.producers.items():
    #             for producer in producerinstances:
    #                 producers.append([child.key, producer.key])
    #         parents["children"].append(self._nodechildren(
    #             service, {"children": [], "name": servicekey}, producers))
    #     self._servicesTree['parentchild'] = parents
    #     self._servicesTree['producerconsumer'] = producers
    #     return self._servicesTree

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
        for service_model in self.db.services.find(name=name, actor=actor, state=state, parent=parent, producer=producer):
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

    def blueprintExecute(self, path="", content="", role="", instance=""):
        bp = None
        if path == "" and content == "":
            for bp in self.blueprints:
                if not bp.is_valid:
                    self.logger.warning("blueprint %s not executed because it doesn't have a valid format" % bp.path)
                    return
                bp.load(role=role, instance=instance)
        else:
            bp = Blueprint(self, path=path, content=content)
            # self._blueprints[bp.path] = bp
            if not bp.is_valid:
                return
            bp.load(role=role, instance=instance)
        self.init(role=role, instance=instance)

        def to_camel_case(snake_str):
            components = snake_str.split('_')
            return components[0] + "".join(x.title() for x in components[1:])

        templates = []

        # update repo data
        for sv in self.services:
            actor_name, instance = sv.model.__str__().split('!')
            service_name = "%s__%s" % (actor_name, instance)
            service_data = j.data.serializer.json.loads(sv.model.dataJSON)
            if bp is not None:
                for model in bp.models:
                    model_data = model.get(service_name, None)
                    if not model_data:
                        continue
                    for key, val in model_data.items():
                        if '_' not in key:
                            continue
                        model_data[to_camel_case(key)] = model_data.pop(key)

                    if service_data != model_data:
                        templates.append(actor_name)

        for n in templates:
            template = self.templateGet(name=n)
            actor = self.actorGet(name=n)
            actor._initFromTemplate(template)

        print("blueprint done")

    def blueprintGet(self, bname):
        bpath = os.path.join(self.path, "blueprints", bname)

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
            producer_candidates = service.getProducersRecursive(producers=set(), callers=set(), action=action, producerRoles=producerRoles)
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
        raise j.exceptions.Input('No run with key %s found' % runkey)

    def runsList(self):
        """
        list Runs on repo
        """
        runs = j.core.jobcontroller.db.runs.find(repo=self.model.key)

        return runs

    def findScheduledActions(self):
        """
        Walk over all servies and look for action with state scheduled.
        It then creates actions chains for all schedules actions.
        """
        result = {}
        for service_model in self.db.services.find():
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
        run = j.core.jobcontroller.newRun(repo=self.model.key)

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
