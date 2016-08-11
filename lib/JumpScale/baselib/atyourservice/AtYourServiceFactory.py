from JumpScale import j

# from JumpScale.baselib.atyourservice.actor import actor
# from JumpScale.baselib.atyourservice.Service import Service, loadmodule
from JumpScale.baselib.atyourservice.ActorTemplate import ActorTemplate

from JumpScale.baselib.atyourservice.ActionsBaseNode import ActionsBaseNode
from JumpScale.baselib.atyourservice.ActionsBaseMgmt import ActionsBaseMgmt
from JumpScale.baselib.atyourservice.ActionMethodDecorator import ActionMethodDecorator

from JumpScale.baselib.atyourservice.AtYourServiceRepo import AtYourServiceRepo

from JumpScale.baselib.atyourservice.AtYourServiceTester import AtYourServiceTester
from JumpScale.baselib.atyourservice.AtYourServiceDB import AtYourServiceDBFactory


import colored_traceback

# THINK NO LONGER NEEDED
# try:
#     from JumpScale.baselib.atyourservice.AtYourServiceSandboxer import *
# except:
#     pass

import os


import sys
if "." not in sys.path:
    sys.path.append(".")


colored_traceback.add_hook(always=True)


class AtYourServiceFactory:

    def __init__(self):
        self.__jslocation__ = "j.atyourservice"

        self._init = False

        self._domains = []
        self._templates = {}
        self._templateRepos = {}

        # self._sandboxer = None

        self._type = None

        self.indocker = False

        # self.sync = AtYourServiceSync()

        self.debug = j.core.db.get("atyourservice.debug") == 1

        self.logger = j.logger.get('j.atyourservice')

        self._test = None

        self.db = AtYourServiceDBFactory()

    def _doinit(self, force=False):

        if force:
            self.reset()

        if self._init is False:

            if j.sal.fs.exists(path="/etc/my_init.d"):
                self.indocker = True

            # see if all specified ays templateRepo's are downloaded
            # if we don't have write permissin on /opt don't try do download service templates
            templateRepos = j.do.getGitReposListLocal()

            codeDir = j.tools.path.get(j.dirs.codeDir)
            if codeDir.access(os.W_OK):
                # can access the opt dir, lets update the atyourservice
                # metadata

                global_templates_repos = j.application.config.getDictFromPrefix("atyourservice.metadata")

                new = False
                for domain in list(global_templates_repos.keys()):
                    url = global_templates_repos[domain]['url']
                    if url.strip() == "":
                        raise j.exceptions.RuntimeError("url cannot be empty")
                    branch = global_templates_repos[domain].get('branch', 'master')
                    templateReponame = url.rpartition("/")[-1]
                    if templateReponame not in list(templateRepos.keys()):
                        j.do.pullGitRepo(url, dest=None, depth=1, ignorelocalchanges=False, reset=False, branch=branch)
                        new = True

                if new:
                    # if we downloaded then we need to update the list
                    templateRepos = j.do.getGitReposListLocal()

            # load global templates
            for domain, repo_info in global_templates_repos.items():
                _, _, _, _, repo_path, _ = j.do.getGitRepoArgs(repo_info['url'])
                gitrepo = j.clients.git.get(repo_path, check_path=False)
                # self._templates.setdefault(gitrepo.name, {})
                for templ in self._actorTemplatesGet(gitrepo, repo_path):
                    self._templates[templ.name] = templ

            self._init = True
            self.reposLoad()

        self._init = True

    def reset(self):
        for templateRepo in self._templateRepos.values():
            templateRepo._templates = {}
            templateRepo._services = {}
        self._templateRepos = {}
        self._domains = []
        self._templates = {}
        j.dirs._ays = None
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

    def _actorTemplatesGet(self, gitrepo, path="", result=[], ays_in_path_check=True):
        """
        path is absolute path (if specified)
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
            for aysfile in tocheck:
                if j.sal.fs.exists('%s/%s' % (path, aysfile)):
                    return True
            return False

        if isValidTemplate(path):
            templ = ActorTemplate(gitrepo, path)
            if templ.name in self._templates:
                if path != self._templates[templ.name].path:
                    self.logger.debug('found %s in %s and %s' % (templ.name, path, self._templates[templ.name].path))
                    raise j.exceptions.Input("Found double template: %s" % templ.name)
            result.append(templ)
        else:
            # not ays actor so lets see for subdirs
            for servicepath in j.sal.fs.listDirsInDir(path, recursive=False):
                dirname = j.sal.fs.getBaseName(servicepath)
                if not dirname.startswith("."):
                    result = self._actorTemplatesGet(gitrepo, servicepath, result)

        return result

    def getService(self, key, die=True):
        if key.count("!") != 2:
            raise j.exceptions.Input("key:%s needs to be $repopath!$role!$instance" % key)
        repopath, role, instance = key.split("!", 2)
        if not self.exist(path=repopath):
            if die:
                raise j.exceptions.Input(
                    "service repo %s does not exist, could not retrieve ays service:%s" % (repopath, key))
            else:
                return None
        repo = self.get(path=repopath)
        return repo.getService(role=role, instance=instance, die=die)

    def actorTemplateGet(self, name, die=True):
        """
        get an actor template
        """
        self._doinit()
        if name in self.templates:
            return self.templates[name]
        if die:
            raise j.exceptions.Input("Cannot find template with name:%s" % name)

    def actorTemplateExists(self, name):
        self._doinit()
        if self.templateGet(name, die=False) is None:
            return False
        return True

# REPOS

    def repoCreate(self, path):
        self._doinit()
        if j.sal.fs.exists(path):
            raise j.exceptions.Input("Directory %s already exists. Can't create AYS repo at the same location." % path)
        j.sal.fs.createDir(path)
        j.sal.fs.createEmptyFile(j.sal.fs.joinPaths(path, '.ays'))
        j.sal.fs.createDir(j.sal.fs.joinPaths(path, 'actorTemplates'))
        j.sal.fs.createDir(j.sal.fs.joinPaths(path, 'blueprints'))
        j.tools.cuisine.local.core.run('git init')
        j.sal.nettools.download(
            'https://raw.githubusercontent.com/github/gitignore/master/Python.gitignore', j.sal.fs.joinPaths(path, '.gitignore'))
        name = j.sal.fs.getBaseName(path)
        git_repo = j.clients.git.get(path)
        self._templateRepos[path] = AtYourServiceRepo(name=name, gitrepo=git_repo, path=path)
        print("AYS Repo created at %s" % path)
        return self._templateRepos[path]

    def reposLoad(self, path=""):
        """
        load templateRepo's from path
        if path not specified then will go from current path, will first walk down if no .ays dirs found then will walk up to find .ays file

        """
        self._doinit()
        if path == "":
            path = j.sal.fs.getcwd()

        if j.sal.fs.exists(path=j.sal.fs.joinPaths(path, ".ays")):
            # are in root of ays dir
            self.repoLoad(path)
            return

        # WALK down, find repo's below
        res = (root for root, dirs, files in os.walk(path) if '.ays' in files)
        res = [str(item) for item in res]

        if len(res) == 0:
            # now walk up & see if we find .ays in dir above
            while path != "":
                if j.sal.fs.exists(path=j.sal.fs.joinPaths(path, ".ays")):
                    self.repoLoad(path)
                    return
                path = j.sal.fs.getParent(path)
                path = path.strip("/").strip()

        if len(res) == 0:
            # did not find ays dir up or down
            j.logger.log('No AYS repos found in %s. need to find a .ays file in root of aysrepo, did walk up & down' % path)
        #     raise j.exceptions.Input("Cannot find AYS repo in:%s, need to find a .ays file in root of aysrepo, did walk up & down." % path)

        # now load the repo's
        for path in res:
            self.repoLoad(path)

    def repoLoad(self, path):
        self._doinit()

        if not j.sal.fs.exists(path=path):
            raise j.exceptions.Input("Cannot find ays templateRepo on path:%s" % path)
        gitpath = j.clients.git.findGitPath(path)
        gitrepo = j.clients.git.get(gitpath, check_path=False)

        name = j.sal.fs.getBaseName(path)

        if name in self._templateRepos:
            raise j.exceptions.Input(
                "AYS templateRepo with name:%s already exists at %s, cannot have duplicate names." % (name, path))

        self._templateRepos[path] = AtYourServiceRepo(name, gitrepo, path)

    def repoGet(self, path=""):
        """
        @return:    @AtYourServiceRepo object
        """
        self._doinit()

        name = j.sal.fs.getBaseName(path)
        if path:
            if path not in self._templateRepos:
                if j.sal.fs.exists(path) and j.sal.fs.isDir(path):
                    self._templateRepos[path] = AtYourServiceRepo(
                        name=name, gitrepo=j.clients.git.findGitPath(path), path=path)

        else:
            # we want to retrieve  templateRepo by name
            result = [templateRepo for templateRepo in self._templateRepos.values(
            ) if templateRepo.name == name]
            if not result:
                path = j.sal.fs.getcwd()
                if not name:
                    name = j.sal.fs.getBaseName(path)
                self._templateRepos[path] = AtYourServiceRepo(name, gitrepo=j.clients.git.findGitPath(path), path=path)
            elif len(result) > 1:
                msg = "Multiple AYS templateRepos with name %s found under locations [%s]. Please use j.atyourservice.get(path=<path>) instead" % \
                    (name, ','.join(
                        [templateRepo.path for templateRepo in result]))
                raise j.exceptions.RuntimeError(msg)
            else:
                path = result[0].path

        return self._templateRepos[path]


# SERVICE

    def serviceGet(self, key, die=True):
        self._doinit()
        if key.count("!") != 2:
            raise j.exceptions.Input(
                "key:%s needs to be $templateReponame!$role!$instance" % key)
        templateReponame, role, instance = key.split("!", 2)
        if not self.templateRepoExist(name=templateReponame):
            if die:
                raise j.exceptions.Input(
                    "service templateRepo %s does not exist, could not retrieve ays service:%s" % (templateReponame, key))
            else:
                return None
        templateRepo = self.get(name=templateReponame)
        return templateRepo.getService(role=role, instance=instance, die=die)


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

    def getActionsBaseClassNode(self):
        return ActionsBaseNode

    def getActionsBaseClassMgmt(self):
        return ActionsBaseMgmt

    def getActionMethodDecorator(self):
        return ActionMethodDecorator

    # def telegramBot(self, token, start=True):
    #     from JumpScale.baselib.atyourservice.telegrambot.TelegramAYS import TelegramAYS
    #     bot = TelegramAYS(token)
    #     if start:
    #         bot.run()
    #     return bot

    # def _parseKey(self, key):
    #     """
    #     @return (domain,name,instance,role)
    #     """
    #     key = key.lower()
    #     if key.find("|") != -1:
    #         domain, name = key.split("|")
    #     else:
    #         domain = ""
    #         name = key

    #     if name.find("@") != -1:
    #         name, role = name.split("@", 1)
    #         role = role.strip()
    #     else:
    #         role = ""

    #     if name.find("!") != -1:
    #         # found instance
    #         name, instance = name.split("!", 1)
    #         instance = instance.strip()
    #         if domain == '':
    #             role = name
    #             name = ''
    #     else:
    #         instance = ""

    #     name = name.strip()

    #     if role == "":
    #         if name.find('.') != -1:
    #             role = name.split(".", 1)[0]
    #         else:
    #             role = name

    #     domain = domain.strip()
    #     return (domain, name, instance, role)
