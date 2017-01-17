from JumpScale import j

from JumpScale.baselib.atyourservice81.ActorTemplate import ActorTemplate
from JumpScale.baselib.atyourservice81 import ActionsBase
from JumpScale.baselib.atyourservice81.AtYourServiceRepo import AtYourServiceRepo
from JumpScale.baselib.atyourservice81.AtYourServiceTester import AtYourServiceTester

import colored_traceback
import os
import sys
if "." not in sys.path:
    sys.path.append(".")

import inspect

colored_traceback.add_hook(always=True)


class AYSGitRepo():

    def __init__(self, path, templates=False, services=False):
        self.git = j.clients.git.get(path)
        self.templates = templates
        self.services = services


class AtYourServiceFactory:

    def __init__(self):
        self.__jslocation__ = "j.atyourservice"

        self._init = False

        self._config = None

        self._domains = []

        self._templates = {}

        self._gitrepos = {}

        self._repos = {}

        self._type = None

        self.indocker = False

        self.debug = j.core.db.get("atyourservice.debug") == 1

        self.logger = j.logger.get('j.atyourservice')

        self._test = None

        self.baseActions = {}

    @property
    def config(self):
        if self._config is None:
            cfg = j.application.config.jumpscale['ays']
            if 'redis' not in cfg:
                cfg.update({'redis': j.core.db.config_get('unixsocket')})
            self._config = cfg
        return self._config

    def test(self):
        r = self.get()
        print(r.servicesFind())

        from IPython import embed
        print("DEBUG NOW ays test")
        embed()
        raise RuntimeError("stop debug here")

    def testTemplates(self):
        for key, r in self.repos.items():
            print(r)
            break

        for key, t in self.actorTemplates.items():
            print(t.role)
            print(t.schemaCapnpText)
            print(t.schema)
            print(t.recurringConfig)
            print(t.consumptionConfig)
            print(t.parentConfig)
            print(t.eventsConfig)
            print(t.getActorModelObj(r))

            break

    def _doinit(self, force=False):

        if force:
            self.reset()

        if self._init is False:

            if j.sal.fs.exists(path="/etc/my_init.d"):
                self.indocker = True

            # load global templates
            for domain, repo_info in global_templates_repos.items():
                _, _, _, _, repo_path, _ = j.do.getGitRepoArgs(repo_info['url'])
                gitrepo = j.clients.git.get(repo_path, check_path=False)
                # self._templates.setdefault(gitrepo.name, {})
                for templ in self._actorTemplatesGet(gitrepo, repo_path):
                    self._templates[templ.name] = templ

            self._reposLoad()

            self._init = True

        self._init = True

    def reset(self):
        self._templates = {}
        self._templateRepos = {}
        self._domains = []
        self._templates = {}
        self._init = False

# GIREPOS's
    @property
    def gitrepos(self):
        """
        find ays repos
        """
        if self._gitrepos == {}:
            self.repos
            self.actorTemplates
        return self._gitrepos

    def gitrepoAdd(self, path):
        """
        path can be any path in a git repo
        will look for the directory with .git and create a AYSGitRepo object if it doesn't exist yet
        return None when no git repo found
        """
        while not j.sal.fs.exists(j.sal.fs.joinPaths(path, ".git")) and path != "":
            # print(path)
            path = j.sal.fs.getParent(path).rstrip("/").strip()

        if path == "":
            # did not find a git parent
            return None
        else:
            if path not in self._gitrepos:
                print("New AYS GIT REPO:%s" % path)
                ar = AYSGitRepo(path)
                self._gitrepos[path] = ar
            return self._gitrepos[path]

# TEMPLATES

    def actorTemplatesUpdate(self):

        from IPython import embed
        print("DEBUG NOW 9898")
        embed()
        raise RuntimeError("stop debug here")

        repos_path = (root for root, dirs, files in os.walk(path, followlinks=False) if '.ays' in files)

        from IPython import embed
        print("DEBUG NOW 98989")
        embed()
        raise RuntimeError("stop debug here")

        localGitRepos = j.clients.git.getGitReposListLocal()

        # see if all specified ays templateRepo's are downloaded
        # if we don't have write permission on /opt don't try do download service templates
        codeDir = j.tools.path.get(j.dirs.CODEDIR)
        if codeDir.access(os.W_OK):
            # can access the opt dir, lets update the atyourservice
            # metadata

            global_templates_repos = j.atyourservice.config['metadata']

            for domain, info in global_templates_repos.items():
                url = info['url']
                if url.strip() == "":
                    raise j.exceptions.RuntimeError("url cannot be empty")
            branch = info.get('branch', 'master')
            templateReponame = url.rpartition("/")[-1]
            if templateReponame not in list(localGitRepos.keys()):
                j.do.pullGitRepo(url, dest=None, depth=1, ignorelocalchanges=False, reset=False, branch=branch)

    @property
    def actorTemplates(self):
        """
        these are actor templates usable for all ays templateRepo's
        """

        # look for ays repos which have services, actors, ...
        if self._templates == {}:
            path = j.sal.fs.pathNormalize(j.dirs.CODEDIR)

            res = []

            def returnFalse(path, arg):
                return False

            # check if this is already an actortemplate dir, if not no need to recurse
            def isValidTemplate(path):
                dirname = j.sal.fs.getBaseName(path)
                tocheck = ['config.yaml', "schema.capnp"]
                if dirname.startswith("_") or dirname.startswith("."):
                    return False
                for aysfile in tocheck:
                    if j.sal.fs.exists('%s/%s' % (path, aysfile)):
                        if not dirname.startswith("_"):
                            return True
                        else:
                            return False
                return False

            def callbackFunctionDir(path, arg):
                # print(path)
                # base = j.sal.fs.getBaseName(path)
                if arg[3] != "" and isValidTemplate(path):
                    # print(path)
                    arg[1].append(path)

            def callbackForMatchDir(path, arg):
                base = j.sal.fs.getBaseName(path)
                if base.startswith("."):
                    return False
                # if base in [".git", ".hg", ".github"]:
                #     return False
                if base.startswith("ays_"):
                    arg[2] = path
                elif arg[2] != "":
                    if not path.startswith(arg[2]):
                        arg[2] = ""
                        # because means that ays repo is no longer our parent

                if base == "templates" and arg[2] != "":
                    arg[3] = path
                elif arg[3] != "":
                    if not path.startswith(arg[3]):
                        arg[3] = ""
                        # because means that  is no longer our parent

                depth = len(j.sal.fs.pathRemoveDirPart(path, arg[0]).split("/"))
                # print("%s:%s" % (depth, j.sal.fs.pathRemoveDirPart(path, arg[0])))
                if depth < 4:
                    return True
                elif depth < 8 and arg[3] != "":
                    return True
                return False

            j.sal.fswalker.walkFunctional(path, callbackFunctionFile=None, callbackFunctionDir=callbackFunctionDir, arg=[path, res, "", ""],
                                          callbackForMatchDir=callbackForMatchDir, callbackForMatchFile=returnFalse)
            for ppath in res:
                gitrepo = self.gitrepoAdd(path=ppath)
                self._actorTemplateLoad(path=ppath, gitrepo=gitrepo)

        return self._templates

    def actorTemplatesAdd(self, templateRepos):
        """
        update the git templateRepo that contains the service templates
        args:
            templateRepos : list of dict of templateRepos to update, if empty, all templateRepos are updated
                    {
                        'url' : 'http://github.com/account/templateRepo',
                        'branch' : 'master'
                    },
                    {
                        'url' : 'http://github.com/account/templateRepo',
                        'tag' : 'atag'
                    },

        """
        for item in templateRepos:
            if 'branch' in item:
                branch = item["branch"]
            else:
                branch = "master"
            if 'tag' in item:
                tag = item["tag"]
            else:
                tag = ""

            self.actorTemplateAdd(item["url"], branch=branch, tag=tag)
            j.do.pullGitRepo(url=templateRepo['url'], branch=branch, tag=tag)

        self.reset()

    def actorTemplatesFind(self, name="", domain="", role=''):
        res = []
        for template in self.actorTemplates.values():
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

    def _actorTemplateLoad(self, gitrepo, path):
        """
        path is absolute path (if specified)
        this is used in factory as well as in repo code, this is the code which actually finds the templates
        """
        if path == "":
            path = gitrepo.path

        if not j.sal.fs.exists(path=path):
            raise j.exceptions.Input("Cannot find path for ays templates:%s" % path)

        templ = ActorTemplate(path=path, gitrepo=gitrepo)
        if templ.name in self._templates:
            if path != self._templates[templ.name].path:
                msg = 'Found duplicate template:found %s in \n- %s and \n- %s' % (
                    templ.name, path, self._templates[templ.name].path)
                self.logger.debug(msg)
                raise j.exceptions.Input(msg)
        else:
            at = ActorTemplate(path=path, gitrepo=gitrepo)
            self._templates[at.name] = at

# REPOS

    @property
    def repos(self):
        """
        find ays repos
        """

        # look for ays repos which have services, actors, ...
        if self._repos == {}:
            path = j.sal.fs.pathNormalize(j.dirs.CODEDIR)

            res = []

            def returnFalse(path, arg):
                return False

            def callbackFunctionDir(path, arg):
                # print(path)
                if j.sal.fs.exists("%s/.ays" % path):
                    print(path)
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
                                          callbackForMatchDir=callbackForMatchDir, callbackForMatchFile=returnFalse)
            # now we found all dirs with .ays

            for ppath in res:
                if ppath not in self._repos:
                    obj = AtYourServiceRepo(ppath)
                    self._repos[obj.name] = obj

        return self._repos

    def repoCreate(self, path, git_url=''):
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

        model = self._repos.new()
        model.path = path
        model.save()

        git_repo = j.clients.git.get(path, check_path=False)
        self._templateRepos[path] = AtYourServiceRepo(name=name, gitrepo=git_repo, path=path)
        print("AYS Repo created at %s" % path)
        return self._templateRepos[path]

    def repoGet(self, path=""):
        """
        start from current dir & walk up till .ays
        if found return the repo at this location,
        if not raise error
        """
        if path == "":
            path = j.sal.fs.getcwd()
        while path != "":
            if j.sal.fs.exists(path=j.sal.fs.joinPaths(path, ".ays")):
                return self._repoLoad(path)
            path = j.sal.fs.getParent(path)
            path = path.strip("/").strip()
        j.events.inputerror_critical("Cannot find ays repo starting from '%s'" % path)

    def reposLoad(self, path=""):
        """
        load templateRepo's from path
        will walk down and for each dir where .ays found will load the repo
        """

        if not path:
            path = j.dirs.CODEDIR

        if j.sal.fs.exists(path=j.sal.fs.joinPaths(path, ".ays")):
            # are in root of ays dir
            self._repoLoad(path)
            return

        # WALK down, find repo's below
        path = j.sal.fs.pathNormalize(path)
        repos_path = (root for root, dirs, files in os.walk(path) if '.ays' in files)

        repos = []
        for repo_path in repos_path:
            repos.append(self._repoLoad(repo_path))
        return repos

    def _repoLoad(self, path):

        if not j.sal.fs.exists(path=path):
            raise j.exceptions.NotFound("Cannot find ays templateRepo on path:%s" % path)
        gitpath = j.clients.git.findGitPath(path)
        gitrepo = j.clients.git.get(gitpath, check_path=False)

        name = j.sal.fs.getBaseName(path)

        if name in self._templateRepos:
            raise j.exceptions.Input(
                "AYS templateRepo with name:%s already exists at %s, cannot have duplicate names." % (name, path))

        # if the repo we are curently loading in not in db yet. add it.
        models = self._repos.find(path)

        if len(models) <= 0:
            model = self._repos.new()
            model.path = path
            model.save()
        else:
            model = models[0]

        repo = AtYourServiceRepo(name, gitrepo, path, model=model)
        # self._repos[name] = repo

        return repo

    def get(self):
        """
        returns repo we are in
        """
        path = j.sal.fs.getcwd()
        return self.repoGet(path=path)

    def repoGet(self, path):
        """
        if repo doesn't exist at path, try to create one

        @return:    @AtYourServiceRepo object
        """
        self._doinit()

        repo_models = self._repos.find(path)
        if len(repo_models) <= 0:
            raise j.exceptions.Input(message="Could not find repo in path:%s" %
                                     path, level=1, source="", tags="", msgpub="")

        repo = self._repoLoad(repo_models[0].path)

        return repo

    def repoGetByKey(self, key):
        self._doinit()

        repo_model = self._repos.get(key)
        if repo_model is None:
            raise j.exceptions.Input(message="Could not find repo in path:%s" %
                                     path, level=1, source="", tags="", msgpub="")

        repo = self._repoLoad(repo_model.path)

        return repo


# FACTORY

    def getAYSTester(self, name="fake_IT_env"):
        self._init()
        return AtYourServiceTester(name)

    @property
    def domains(self):
        """
        actor domains
        """
        self._doinit()
        return self._domains

    def _loadActionBase(self):
        """
        load all the basic actions for atyourservice
        """
        if self.baseActions == {}:
            for method in [item[1] for item in inspect.getmembers(ActionsBase) if item[0][0] != "_"]:
                action_code_model = j.core.jobcontroller.getActionObjFromMethod(method)
                if not j.core.jobcontroller.db.actions.exists(action_code_model.key):
                    # will save in DB
                    action_code_model.save()
                self.baseActions[action_code_model.dbobj.name] = action_code_model, method
