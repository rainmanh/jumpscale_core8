from JumpScale import j

from JumpScale.baselib.atyourservice81.ActorTemplate import ActorTemplate
from JumpScale.baselib.atyourservice81 import ActionsBase
from JumpScale.baselib.atyourservice81.AtYourServiceRepo import AtYourServiceRepo
from JumpScale.baselib.atyourservice81.AtYourServiceTester import AtYourServiceTester
from JumpScale.baselib.atyourservice81.models import ModelsFactory

import colored_traceback
import os
import sys
if "." not in sys.path:
    sys.path.append(".")

import inspect

colored_traceback.add_hook(always=True)


class AtYourServiceFactory:

    def __init__(self):
        self.__jslocation__ = "j.atyourservice"

        self._init = False

        self._config = None

        self._domains = []
        self._templates = {}
        self._templateRepos = {}
        self._repos = {}

        self._type = None

        self.indocker = False

        self.debug = j.core.db.get("atyourservice.debug") == 1

        self.logger = j.logger.get('j.atyourservice')

        self._repodb = None

        self._test = None

        self.baseActions = {}

    @property
    def config(self):
        if self._config is None:
            config_path = j.sal.fs.joinPaths(j.dirs.cfgDir, 'ays/ays.config')
            if not j.sal.fs.exists(config_path):
                self._config = {'redis': j.core.db.config_get('unixsocket'),
                                'metadata': [{'jumpscale': {'url': 'https://github.com/Jumpscale/ays_jumpscale8', 'branch': 'master'}}]}
                return self._config
            cfg = j.data.serializer.toml.load(config_path)
            if 'redis' not in cfg:
                cfg.update({'redis': j.core.db.config_get('unixsocket')})
            if 'metadata' not in cfg:
                cfg.update({'metadata': [{'jumpscale': {'url': 'https://github.com/Jumpscale/ays_jumpscale8', 'branch': 'master'}}]})
            j.atyourservice._config = cfg
        return self._config

    @property
    def repodb(self):
        if self._repodb is None:
            self._repodb = ModelsFactory().repo
        return self._repodb

    def test(self):
        r = self.get()
        print(r.servicesFind())

        from IPython import embed
        print("DEBUG NOW ays test")
        embed()
        raise RuntimeError("stop debug here")

    def _doinit(self, force=False):

        if force:
            self.reset()

        if self._init is False:

            if j.sal.fs.exists(path="/etc/my_init.d"):
                self.indocker = True

            localGitRepos = j.do.getGitReposListLocal()

            # see if all specified ays templateRepo's are downloaded
            # if we don't have write permissin on /opt don't try do download service templates
            codeDir = j.tools.path.get(j.dirs.codeDir)
            if codeDir.access(os.W_OK):
                # can access the opt dir, lets update the atyourservice
                # metadata

                global_templates_repos = j.atyourservice.config['metadata']

                for item in global_templates_repos:
                    for domain, info in item.items():
                        url = info['url']
                        if url.strip() == "":
                            raise j.exceptions.RuntimeError("url cannot be empty")
                    branch = info.get('branch', 'master')
                    templateReponame = url.rpartition("/")[-1]
                    if templateReponame not in list(localGitRepos.keys()):
                        j.do.pullGitRepo(url, dest=None, depth=1, ignorelocalchanges=False, reset=False, branch=branch)

            # load global templates
            for item in global_templates_repos:
                for domain, repo_info in item.items():
                    _, _, _, _, repo_path, _ = j.do.getGitRepoArgs(repo_info['url'])
                    gitrepo = j.clients.git.get(repo_path, check_path=False)
                    # self._templates.setdefault(gitrepo.name, {})
                    for templ in self._actorTemplatesGet(gitrepo, repo_path):
                        self._templates[templ.name] = templ

            self._reposLoad()

            self._init = True

        self._init = True

    def reset(self):
        self._templateRepos = {}
        self._repos = {}
        self._domains = []
        self._templates = {}
        self._init = False


# TEMPLATES

    @property
    def actorTemplates(self):
        """
        these are actor templates usable for all ays templateRepo's
        """
        if self._templates == {}:
            self._doinit()
        return self._templates

    def actorTemplatesUpdate(self, templateRepos=[]):
        """
        update the git templateRepo that contains the service templates
        args:
            templateRepos : list of dict of templateRepos to update, if empty, all templateRepos are updated
                    {
                        'url' : 'http://github.com/account/templateRepo',
                        'branch' : 'master'
                    }
        """
        if len(templateRepos) == 0:
            metadata = j.application.config.getDictFromPrefix(
                'atyourservice.metadata')
            templateRepos = list(metadata.values())

        for templateRepo in templateRepos:
            branch = templateRepo[
                'branch'] if 'branch' in templateRepo else 'master'
            j.do.pullGitRepo(url=templateRepo['url'], branch=branch)

        self._doinit(True)

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

    def _actorTemplatesGet(self, gitrepo, path="", result=[], aysrepo=None):
        """
        path is absolute path (if specified)
        this is used in factory as well as in repo code, this is the code which actually finds the templates
        """
        if path == "":
            path = gitrepo.path

        if not j.sal.fs.exists(path=path):
            raise j.exceptions.Input("Cannot find path for ays templates:%s" % path)

        dirname = j.sal.fs.getBaseName(path)

        # check if this is already an actortemplate dir, if not no need to recurse
        def isValidTemplate(path):
            tocheck = ['schema.hrd', 'service.hrd', 'actions_mgmt.py',
                       'actions_node.py', 'model.py', 'actions.py', "model.capnp"]
            dirname = j.sal.fs.getBaseName(path)
            for aysfile in tocheck:
                if j.sal.fs.exists('%s/%s' % (path, aysfile)):
                    if not dirname.startswith("_"):
                        return True
                    else:
                        return False
            return False

        if isValidTemplate(path):
            templ = ActorTemplate(gitrepo, path, aysrepo=aysrepo)
            if aysrepo is None:  # no need to check if in repo because then there can be doubles
                if templ.name in self._templates:
                    if path != self._templates[templ.name].path:
                        self.logger.debug('found %s in %s and %s' %
                                          (templ.name, path, self._templates[templ.name].path))
                        raise j.exceptions.Input("Found double template: %s" % templ.name)
            result.append(templ)
        else:
            # not ays actor so lets see for subdirs
            for servicepath in j.sal.fs.listDirsInDir(path, recursive=False):
                dirname = j.sal.fs.getBaseName(servicepath)
                if not dirname.startswith("."):
                    result = self._actorTemplatesGet(gitrepo, servicepath, result, aysrepo=aysrepo)

        return result

# REPOS

    def reposDiscover(self, path=None):
        """
        Walk over FS. Register AYS repos to DB
        """
        if not path:
            path = j.dirs.codeDir
        path = j.sal.fs.pathNormalize(path)
        repos_path = (root for root, dirs, files in os.walk(path) if '.ays' in files)

        repos = []
        for repo_path in repos_path:
            repos.append(self._repoLoad(repo_path))

        return repos

    def reposList(self):
        repos = []
        for model in self.repodb.find():
            repos.append(model.objectGet())
        return repos

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

        model = self.repodb.new()
        model.path = path
        model.save()

        git_repo = j.clients.git.get(path, check_path=False)
        self._templateRepos[path] = AtYourServiceRepo(name=name, gitrepo=git_repo, path=path)
        print("AYS Repo created at %s" % path)
        return self._templateRepos[path]

    def _reposLoad(self, path=""):
        """
        load templateRepo's from path
        if path not specified then will go from current path, will first walk down if no .ays dirs found then will walk up to find .ays file
        """
        if path == "":
            path = j.sal.fs.getcwd()

        if j.sal.fs.exists(path=j.sal.fs.joinPaths(path, ".ays")):
            # are in root of ays dir
            self._repoLoad(path)
            return

        # WALK down, find repo's below
        res = (root for root, dirs, files in os.walk(path) if '.ays' in files)
        res = [str(item) for item in res]

        if len(res) == 0:
            # now walk up & see if we find .ays in dir above
            while path != "":
                if j.sal.fs.exists(path=j.sal.fs.joinPaths(path, ".ays")):
                    self._repoLoad(path)
                    return
                path = j.sal.fs.getParent(path)
                path = path.strip("/").strip()

        if len(res) == 0:
            # did not find ays dir up or down
            j.logger.log('No AYS repos found in %s. need to find a .ays file in root of aysrepo, did walk up & down' % path)
        #     raise j.exceptions.Input("Cannot find AYS repo in:%s, need to find a .ays file in root of aysrepo, did walk up & down." % path)

        # now load the repo's
        for path in res:
            self._repoLoad(path)

    def _repoLoad(self, path):

        if not j.sal.fs.exists(path=path):
            raise j.exceptions.Input("Cannot find ays templateRepo on path:%s" % path)
        gitpath = j.clients.git.findGitPath(path)
        gitrepo = j.clients.git.get(gitpath, check_path=False)

        name = j.sal.fs.getBaseName(path)

        if name in self._templateRepos:
            raise j.exceptions.Input(
                "AYS templateRepo with name:%s already exists at %s, cannot have duplicate names." % (name, path))

        # if the repo we are curently loading in not in db yet. add it.
        models = self.repodb.find(path)

        if len(models) <= 0:
            model = self.repodb.new()
            model.path = path
            model.save()
        else:
            model = models[0]

        repo = AtYourServiceRepo(name, gitrepo, path, model=model)
        self._repos[name] = repo

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

        def findRepo(path):
            for key, repo in self._repos.items():
                if repo.path == path:
                    return repo
            return None

        repo = findRepo(path)
        if repo is None:
            # repo does not exist yet
            self._repoLoad(path)
            repo = findRepo(path)

        if repo is None:
            raise j.exceptions.Input(message="Could not find repo in path:%s" %
                                     path, level=1, source="", tags="", msgpub="")

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
                if not j.core.jobcontroller.db.action.exists(action_code_model.key):
                    # will save in DB
                    action_code_model.save()
                self.baseActions[action_code_model.dbobj.name] = action_code_model, method
