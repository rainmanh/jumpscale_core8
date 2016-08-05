from JumpScale import j

from JumpScale.baselib.atyourservice.ServiceRecipe import ServiceRecipe
from JumpScale.baselib.atyourservice.Service import Service, loadmodule
from JumpScale.baselib.atyourservice.ServiceTemplate import ServiceTemplate

from JumpScale.baselib.atyourservice.ActionsBaseNode import ActionsBaseNode
from JumpScale.baselib.atyourservice.ActionsBaseMgmt import ActionsBaseMgmt
from JumpScale.baselib.atyourservice.ActionMethodDecorator import ActionMethodDecorator

from JumpScale.baselib.atyourservice.AtYourServiceRepo import AtYourServiceRepo

from JumpScale.baselib.atyourservice.AtYourServiceTester import AtYourServiceTester

try:
    from JumpScale.baselib.atyourservice.AtYourServiceSandboxer import *
except:
    pass
import os


import sys
if "." not in sys.path:
    sys.path.append(".")

import capnp
import aysmodel_capnp as AYSModel


import colored_traceback
colored_traceback.add_hook(always=True)


class AtYourServiceFactory:

    def __init__(self):
        self.__jslocation__ = "j.atyourservice"

        self._init = False

        self._domains = []
        self._templates = {}
        self._sandboxer = None

        # self.hrd = None

        self._type = None

        self.indocker = False

        # self.sync = AtYourServiceSync()
        # self._reposDone = {}

        self.debug = j.core.db.get("atyourservice.debug") == 1

        self.logger = j.logger.get('j.atyourservice')

        self._repos = {}

        self._test = None

        self.db=j.servers.kvs.getRedisStore("ays") #for now in redis but this will change to tarantool

        self.AYSModel=AYSModel        

    def getTester(self, name="fake_IT_env"):
        return AtYourServiceTester(name)

    def exist(self, path):
        """
        Check if a repo at the given path exist or not, if multiple repos found under that path, an exception is raised

        @param name: name of the repo
        @type name: str

        @returns:   True if exist, Flase if it doesnt, raises exception if mulitple found with the same name
        """
        try:
            result = self.findAYSRepos(path=path)
        except j.exceptions.Input:
            # doesnt exists
            return False

        if len(result) > 1:
            msg = "Multiple AYS repos found under %s: \n%s\n" % (path, '\n'.join(result))
            raise j.exceptions.Input(msg)

        return True

    def get(self, name="", path=""):
        """
        Get a repo by name or path, if repo does not exist, it will be created

        @param name: Name of the repo to retrieve
        @type name: str

        @param path:    Path of the repo
        @type path:     str

        @return:    @AtYourServiceRepo object
        """
        self._doinit()
        if path:
            if path not in self._repos:
                if j.sal.fs.exists(path) and j.sal.fs.isDir(path):
                    if not name:
                        name = j.sal.fs.getBaseName(path)
                    self._repos[path] = AtYourServiceRepo(name, path)

        else:
            # we want to retrieve  repo by name
            result = [repo for repo in self._repos.values() if repo.name == name]
            if not result:
                path = j.sal.fs.getcwd()
                if not name:
                    name = j.sal.fs.getBaseName(path)
                self._repos[path] = AtYourServiceRepo(name, path)
            elif len(result) > 1:
                msg = "Multiple AYS repos with name %s found under locations [%s]. Please use j.atyourservice.get(path=<path>) instead" % \
                        (name, ','.join([repo.basepath for repo in result]))
                raise j.exceptions.RuntimeError(msg)
            else:
                path = result[0].basepath

        return self._repos[path]

    def reset(self):
        for repo in self._repos.values():
            repo._templates = {}
            repo._services = {}
        self._repos = {}
        self._domains = []
        self._templates = {}
        j.dirs._ays = None
        self._init = False


    @property
    def sandboxer(self):
        if self._sandboxer is None:
            self._sandboxer = AtYourServiceSandboxer()
        return self._sandboxer

    @property
    def domains(self):
        self._doinit()
        return self._domains

    @property
    def templates(self):
        self._doinit()

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
                if templ.name in self._templates:
                    raise j.exceptions.Input("Found double template: %s" % templ.name)
                self._templates[templ.name] = templ

        if not self._templates:
            self._doinit()

            for domain, domainpath in self.domains:
                # print "load template domain:%s"%domainpath
                load(domain, domainpath)

        return self._templates

    # @property
    # def roletemplates(self):
    #     if self._roletemplates:
    #         return self._roletemplates
    #     templatespaths = [j.sal.fs.joinPaths(self.basepath, '_templates')]
    #     for _, metapath in self._domains:
    #         templatespaths.append(j.sal.fs.joinPaths(metapath, '_templates'))
    #     templatespaths.reverse()

    #     for templatespath in templatespaths:
    #         if j.sal.fs.exists(templatespath):
    #             for roletemplate in j.sal.fs.listDirsInDir(templatespath):
    #                 paths = ['schema_tmpl.hrd', 'actions_tmpl_mgmt.py', 'actions_tmpl_node.py']
    #                 rtpaths = [path for path in paths if j.sal.fs.exists(j.sal.fs.joinPaths(templatespath, roletemplate, path))]
    #                 if rtpaths:
    #                     self._roletemplates[j.sal.fs.getBaseName(roletemplate)] = [j.sal.fs.joinPaths(roletemplate, rtpath) for rtpath in rtpaths]
    #     return self._roletemplates

    def _doinit(self):

        if self._init is False:

            # if we don't have write permissin on /opt don't try do download service templates
            opt = j.tools.path.get('/opt')
            if not opt.access(os.W_OK):
                self._init = True
                return

            if j.sal.fs.exists(path="/etc/my_init.d"):
                self.indocker = True

            # always load base domaim
            items = j.application.config.getDictFromPrefix("atyourservice.metadata")
            repos = j.do.getGitReposListLocal()

            for domain in list(items.keys()):
                url = items[domain]['url']
                if url.strip() == "":
                    raise j.exceptions.RuntimeError("url cannot be empty")
                branch = items[domain].get('branch', 'master')
                reponame = url.rpartition("/")[-1]
                if reponame not in list(repos.keys()):
                    dest = j.do.pullGitRepo(url, dest=None, depth=1, ignorelocalchanges=False, reset=False, branch=branch)

                repos = j.do.getGitReposListLocal()

                dest = repos[reponame]
                self._domains.append((domain, dest))

            self._init = True

    def createAYSRepo(self, path):
        j.sal.fs.createDir(path)
        j.sal.fs.createEmptyFile(j.sal.fs.joinPaths(path, '.ays'))
        j.sal.fs.createDir(j.sal.fs.joinPaths(path, 'servicetemplates'))
        j.sal.fs.createDir(j.sal.fs.joinPaths(path, 'blueprints'))
        j.tools.cuisine.local.core.run('git init')
        j.sal.nettools.download('https://raw.githubusercontent.com/github/gitignore/master/Python.gitignore', j.sal.fs.joinPaths(path, '.gitignore'))
        name = j.sal.fs.getBaseName(path)
        self._repos[path] = AtYourServiceRepo(name, path)
        print("AYS Repo created at %s" % path)
        return self._repos[path]

    def updateTemplates(self, repos=[]):
        """
        update the git repo that contains the service templates
        args:
            repos : list of dict of repos to update, if empty, all repos are updated
                    {
                        'url' : 'http://github.com/account/repo',
                        'branch' : 'master'
                    }
        """
        if len(repos) == 0:
            metadata = j.application.config.getDictFromPrefix('atyourservice.metadata')
            repos = list(metadata.values())

        for repo in repos:
            branch = repo['branch'] if 'branch' in repo else 'master'
            j.do.pullGitRepo(url=repo['url'], branch=branch)

    def getActionsBaseClassNode(self):
        return ActionsBaseNode

    def getActionsBaseClassMgmt(self):
        return ActionsBaseMgmt

    def getActionMethodDecorator(self):
        return ActionMethodDecorator

    def getBlueprint(self, aysrepo, path):
        return Blueprint(aysrepo, path)

    def findTemplates(self, name="", domain="", role=''):
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

    def findAYSRepos(self, path=""):
        #default do NOT run over all code repo's
        if path=="":
            path=j.sal.fs.getcwd()
        res= (root for root, dirs, files in os.walk(path) if '.ays' in files)
        res=[str(item) for item in res]
        if len(res)==0:
            raise j.exceptions.Input("Cannot find AYS repo in:%s, need to find a .ays file in root of ays repo."%path)
        return res

    def getService(self, key, die=True):
        if key.count("!") != 2:
            raise j.exceptions.Input("key:%s needs to be $reponame!$role!$instance" % key)
        reponame, role, instance = key.split("!", 2)
        if not self.exist(name=reponame):
            if die:
                raise j.exceptions.Input("service repo %s does not exist, could not retrieve ays service:%s" % (reponame, key))
            else:
                return None
        repo = self.get(name=reponame)
        return repo.getService(role=role, instance=instance, die=die)

    def getTemplate(self, name, die=True):
        """
        @param first means, will only return first found template instance
        """
        if name in self.templates:
            return self.templates[name]
        if die:
            raise j.exceptions.Input("Cannot find template with name:%s" % name)
        # if first:
        #     return self.findTemplates(domain=domain, name=name, version=version, role=role, first=first)
        # else:
        #     res = self.findTemplates(domain=domain, name=name, version=version, role=role, first=first)
        #     if len(res) > 1:
        #         if die:
        #             raise j.exceptions.Input("Cannot get ays template '%s|%s (%s)', found more than 1" % (domain, name, version), "ays.gettemplate")
        #         else:
        #             return
        #     if len(res) == 0:
        #         if die:
        #             raise j.exceptions.Input("Cannot get ays template '%s|%s (%s)', did not find" % (domain, name, version), "ays.gettemplate")
        #         else:
        #             return
        #     return res[0]

    def existsTemplate(self, name):
        if self.getTemplate(name, die=False) is None:
            return False
        return True

    def _parseKey(self, key):
        """
        @return (domain,name,instance,role)
        """
        key = key.lower()
        if key.find("|") != -1:
            domain, name = key.split("|")
        else:
            domain = ""
            name = key

        if name.find("@") != -1:
            name, role = name.split("@", 1)
            role = role.strip()
        else:
            role = ""

        if name.find("!") != -1:
            # found instance
            name, instance = name.split("!", 1)
            instance = instance.strip()
            if domain == '':
                role = name
                name = ''
        else:
            instance = ""

        name = name.strip()

        if role == "":
            if name.find('.') != -1:
                role = name.split(".", 1)[0]
            else:
                role = name

        domain = domain.strip()
        return (domain, name, instance, role)

    def __str__(self):
        return self.__repr__()

    # def telegramBot(self, token, start=True):
    #     from JumpScale.baselib.atyourservice.telegrambot.TelegramAYS import TelegramAYS
    #     bot = TelegramAYS(token)
    #     if start:
    #         bot.run()
    #     return bot
