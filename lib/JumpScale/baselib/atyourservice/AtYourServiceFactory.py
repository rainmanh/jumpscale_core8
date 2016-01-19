from JumpScale import j
from ServiceTemplate import ServiceTemplate
from ServiceRecipe import ServiceRecipe
from Service import Service, getProcessDicts
import re
from ActionsBaseMgmt import ActionsBaseMgmt
from ActionsBaseNode import ActionsBaseNode
from Blueprint import Blueprint
from ALog import *
# import AYSdb

from AtYourServiceSync import AtYourServiceSync
try:
    from AtYourServiceSandboxer import *
except:
    pass
import os

# class AYSDB():
#     """
#     @todo
#     """

#     def __init__(self):
#         self.db=j.core.db

#     def index(self,category,key,data):
#         self.db.hset("ays.index.%s"%category,key,data)

#     def reset(self):
#         self.db.delete("ays.domains")
#         self.db.delete("ays.index.service")
#         self.db.delete("ays.index.recipe")
#         self.db.delete("ays.index.template")


class AtYourServiceFactory():

    def __init__(self):
        self.__jslocation__ = "j.atyourservice"

        self._init = False
        self._domains = []
        self.hrd = None
        self._justinstalled = []
        self._type = None
        self._services = {}
        self._templates = []
        self._recipes = []
        self.indocker = False
        self.sync = AtYourServiceSync()
        self._reposDone = {}
        self._todo = []
        self.debug=False
        self._basepath=None
        self._git=None
        self._blueprints=[]
        self._alog=None
        self._runcategory=""
        self._sandboxer=None

        # self._db=AYSDB()

    def reset(self):
        # self._db.reload()
        self._services = {}
        self._templates = []
        self._recipes = []
        self._reposDone = {}
        self._todo = []
        self._git=None
        self._blueprints=[]
        self._alog=None

    @property
    def runcategory(self):
        if self._runcategory=="":
            self._runcategory="deploy"
        return self._runcategory

    @runcategory.setter
    def runcategory(self,val):
        if val!=self._runcategory:
            self.reset()
            self._runcategory=val

    @property
    def alog(self):
        if self._alog==None:
            self._alog=ALog(self.runcategory)
            # self._alog.getNewRun()
        return self._alog

    @property
    def basepath(self):
        if self._basepath==None:
            self.basepath=j.sal.fs.getcwd()
        return self._basepath

    @basepath.setter
    def basepath(self,val):
        self.reset()

        baseDir=val
        while j.sal.fs.joinPaths(baseDir, ".ays") not in j.sal.fs.listFilesInDir(baseDir, recursive=False):
            baseDir=j.do.getParent(baseDir)

            baseDir=baseDir.rstrip("/")

            if baseDir.strip()=="":
                raise RuntimeError("could not find basepath for .ays in %s"%val)

        self._basepath=baseDir
        for item in ["blueprints","recipes","services","servicetemplates"]:
            #make sure basic dirs exist
            j.sal.fs.createDir(j.sal.fs.joinPaths(self._basepath,item))

    @property
    def git(self):
        if self._git==None:
            self._git=j.clients.git.get(basedir=self.basepath)
        return self._git

    @property
    def sandboxer(self):
        if self._sandboxer==None:
            self._sandboxer=AtYourServiceSandboxer()
        return self._sandboxer

    @property
    def type(self):
        if self._type is not None:
            return self._type
        self._type = "n"  # n from normal
        # check if we are in a git directory, if so we will use $thatdir/services as base for the metadata
        configpath = j.dirs.amInAYSRepo()
        if configpath is not None:
            self._type = "c"
        return self._type

    @property
    def domains(self):
        self._doinit()
        return self._domains

    @property
    def templates(self):
        self._doinit()
        def load(domain, path,llist):
            for servicepath in j.sal.fs.listDirsInDir(path, recursive=False):
                dirname = j.do.getBaseName(servicepath)
                # print "dirname:%s"%dirname
                if not (dirname.startswith(".")):
                    load(domain,servicepath,llist)
            # print path
            dirname = j.do.getBaseName(path)
            if dirname.startswith("_"):
                return
            if j.sal.fs.exists("%s/schema.hrd" % path) or j.sal.fs.exists("%s/service.hrd" % path) or j.sal.fs.exists("%s/actions_mgmt.py" % path):
                templ = ServiceTemplate(path, domain=domain)
                llist.append(templ)


        if self._templates==[]:
            self._doinit()

            #load the local service templates
            aysrepopath=j.dirs.amInAYSRepo()
            if aysrepopath!=None:
                # load local templates
                path=j.sal.fs.joinPaths(aysrepopath,"%s/servicetemplates/"%aysrepopath)
                load("ays",path,self._templates)


            for domain, domainpath in self.domains:
                # print "load template domain:%s"%domainpath
                load(domain, domainpath,self._templates)

        return self._templates

    @property
    def recipes(self):
        self._doinit()
        if self._recipes==[]:
            self._doinit()
            aysrepopath=j.dirs.amInAYSRepo()
            if aysrepopath!=None:
                # load local templates
                domainpath=j.sal.fs.joinPaths(aysrepopath,"%s/recipes/"%aysrepopath)
                d=j.tools.path.get(domainpath)
                for item in d.walkfiles("state.hrd"):
                    recipepath=j.do.getDirName(item)
                    self._recipes.append(ServiceRecipe(recipepath))
        return self._recipes

    @property
    def services(self):
        self._doinit()
        if self._services=={}:
            for hrd_path in j.sal.fs.listFilesInDir(j.dirs.ays, recursive=True, \
                filter="instance.hrd", case_sensitivity='os', followSymlinks=True, listSymlinks=False):
                service_path = j.sal.fs.getDirName(hrd_path)
                service = Service(path=service_path, args=None)
                self._services[service.shortkey]=service
        return self._services

    @property
    def blueprints(self):
        """
        """
        if self._blueprints==[]:
            items=j.do.listFilesInDir(self.basepath+"/blueprints")
            items.sort()
            for path in items:
                self._blueprints.append(Blueprint(path))
        return self._blueprints

    def _doinit(self):
        # if we don't have write permissin on /opt don't try do download service templates
        opt = j.tools.path.get('/opt')
        if not opt.access(os.W_OK):
            self._init = True

        if self._init is False:
            j.logger.consolelogCategories.append("AYS")

            # j.do.debug=True

            if j.sal.fs.exists(path="/etc/my_init.d"):
                self.indocker=True

            login=j.application.config.get("whoami.git.login").strip()
            passwd=j.application.config.getStr("whoami.git.passwd").strip()

            # if self.type != "n": #are not on node
                # configpath=j.dirs.amInAYSRepo()
                # # load service templates
                # self._domains.append((j.sal.fs.getBaseName(configpath),"%s/servicetemplates/"%configpath))

            # always load base domaim
            items=j.application.config.getDictFromPrefix("atyourservice.metadata")
            repos=j.do.getGitReposListLocal()

            for domain in list(items.keys()):
                url=items[domain]['url']
                if url.strip()=="":
                    raise RuntimeError("url cannot be empty")
                branch=items[domain].get('branch', 'master')
                reponame=url.rpartition("/")[-1]
                if not reponame in list(repos.keys()):
                    # means git has not been pulled yet
                    if login!="":
                        dest=j.do.pullGitRepo(url,dest=None,login=login,passwd=passwd,depth=1,ignorelocalchanges=False,reset=False,branch=branch)
                    else:
                        dest=j.do.pullGitRepo(url,dest=None,depth=1,ignorelocalchanges=False,reset=False,branch=branch)

                repos=j.do.getGitReposListLocal()

                dest=repos[reponame]
                # print "init %s" % domain
                self._domains.append((domain,dest))

        self._init=True

    def init(self,newrun=True):

        self.reset()

        #make sure the recipe's are loaded & initted
        for bp in self.blueprints:
            bp.loadrecipes()

        #start from clean sheet
        self.reset()

        self.alog
        self.commitGitChanges(action="init_pre",msg='ays changed, commit changed files before deploy of blueprints',precheck=True)

        latestrun=self.alog.newRun(action="init")

        print("init runid:%s"%self.alog.lastRunId)
        commitc=""
        for bp in self.blueprints:
            bp.execute()
            commitc+="\nBlueprint:%s\n"%bp.path
            commitc+=bp.content+"\n"

        self.commitGitChanges(action="init")

        print ("init done")


    def updateTemplatesRepos(self, repos=[]):
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

    def install(self,printonly=False,remember=True):
        self.alog
        #start from clean sheet
        self.init()
        self.do(action="install",printonly=printonly,remember=remember)
        if printonly or remember==False:
            self.alog.removeLastRun()


    def commitGitChanges(self,action="unknown",msg="",precheck=False):
        if len(self.git.getModifiedFiles(True,ignore=["/alog/"]))>0:
            if msg=="":
                msg='ays changed, commit changed files for action:%s'%action
            print(msg)
            repo=self.git.commit(message=msg, addremove=True)
            self.alog.newGitCommit(action=action,githash=repo.hexsha)
        else:
            #@todo will create duplicates will have to fix that
            #git hash is current state
            if not precheck:
                #only do this when no precheck, means we are not cleaning up past
                self.alog.newGitCommit(action=action,githash="")



    def do(self,action="install",printonly=False,remember=True,allservices=False):

        self.alog
        self.commitGitChanges(action=action+"_pre",precheck=True)
        latestrun=self.alog.newRun(action=action)

        if not allservices:
            #we need to find change since last time & make sure that
            #find all services with action with this name and put back on init
            changed,changes=self.alog.getChangedAtYourservices(action=action)
            for service in changed:
                if action in service.actions:
                    actionobj=service.actions[action]
                    actionobj.setState("CHANGED")


        else:
            todo=[item[1] for item in self.services.items()]
            for service in todo:
                actionobj=service.getAction(action)
                if remember==False or printonly:
                    actionobj._state="START"
                else:
                    actionobj.setState("START")

        todo=self.findTodo(action=action)

        step = 1
        error=False
        while todo != []:
            print("execute state changes, nr services to process: %s in step:%s" % (len(todo), step))
            for i in range(len(todo)):
                service = todo[i]
                try:
                    service.runAction(name=action,printonly=printonly)
                except Exception as e:
                    print ("***ERROR %s***\n%s\n"%(service,e))
                    error=True

            step += 1
            if error:
                #don't do other levels, because error on this level
                todo=[]
            else:
                todo=self.findTodo(action=action)

        if printonly:
            remember=False
        if remember==False and error==False:
            self.alog.removeLastRun()
            #revert git
            base=j.dirs.amInAYSRepo()
            self.git.checkout("%s/services/"%base)
            self.git.checkout("%s/recipes/"%base)
        else:
            #this will make sure we will have remembered the last state of this action
            self.commitGitChanges(action=action)


    def findTodo(self,action="install"):
        self.alog
        todo=[]
        for key,service in self.services.items():
            actionrunobj=service.getAction(action)
            if actionrunobj.state!="OK":
                producersWaiting = service.getProducersWaiting(action,set())
                if len(producersWaiting)==0:
                    print("%s waiting for install" % service)
                    todo.append(service)
                elif j.application.debug:
                    print("%s no change in producers" % service)
        return todo

    def checkRevisions(self):
        if len(self.services) == 0:
            self.loadServices()

        for service in self.services:
            service.state.saveRevisions()

    def findTemplates(self, name="", version="",domain="", role='', first=False):
        res = []
        for template in self.templates:
            if not(name == "" or template.name == name):
                # no match continue
                continue
            if not(domain == "" or template.domain == domain):
                # no match continue
                continue
            if not(version == "" or template.version == version):
                # no match continue
                continue
            if not (role == '' or template.role == role):
                # no match continue
                continue
            res.append(template)

        if first:
            if len(res) == 0:
                j.events.inputerror_critical("cannot find service template %s|%s (%s)" % (domain, name, version), "ays.findTemplates")
            return res[0]
        return res

    def findRecipes(self, name="", version="", role='',one=False):
        res = []
        domain="ays"
        for template in self.recipes:
            if not(name == "" or template.name == name):
                # no match continue
                continue
            if not(domain == "" or template.domain == domain):
                # no match continue
                continue
            if not(version == "" or template.version == version):
                # no match continue
                continue
            if not (role == '' or template.role == role):
                # no match continue
                continue
            res.append(template)

        if one:
            if len(res) == 0:
                j.events.inputerror_critical("cannot find ays recipes %s|%s (%s)" % (domain, name, version), "ays.findRecipes")
            if len(res) > 1:
                j.events.inputerror_critical("found 2+ ays recipes %s|%s (%s)" % (domain, name, version), "ays.findRecipes")
            return res[0]

        return res

    def findServices(self, name="", instance="",version="", domain="", parent=None, first=False, role="", node=None, include_disabled=False):
        res = []

        for shortkey,service in self.services.items():
            if service._state and service._state.hrd.getBool('disabled', False) and not include_disabled:
                continue
            if not(name == "" or service.name == name):
                continue
            if not(domain == "" or service.domain == domain):
                continue
            if not(version == "" or service.version == version):
                continue
            if not(instance == "" or service.instance == instance):
                continue
            if not(parent is None or service.parent == parent):
                continue
            if not(role == "" or role == service.role):
                continue
            if not(node is None or service.isOnNode(node)):
                continue
            res.append(service)
        if first:
            if len(res) == 0:
                j.events.inputerror_critical("cannot find service %s|%s:%s (%s)" % (domain, name, instance, version), "ays.findServices")
            return res[0]
        return res

    def findProducer(self, producercategory, instancename):
        for item in self.findServices(instance=instancename):
            if producercategory in item.categories:
                return item

    def new(self,  name="", instance="main",version="",domain="",path=None, parent=None, args={},consume=""):
        """
        will create a new service from template

        @param args are the arguments which will overrule questions of the instance.hrd
        @param consume specifies which ays instances will be consumed
                format $role/$domain|$name!$instance,$role2/$domain2|$name2!$instance2

        """
        recipe = self.getRecipe(name,domain,version)
        obj = recipe.newInstance(instance=instance, path=path, parent=parent, args=args, consume=consume)
        return obj

    def remove(self,  name="", instance="",domain="", role=""):
        for service in self.findServices(domain=domain, name=name, instance=instance, role=role):
            if service in self.services:
                self.services.remove(service)
            j.sal.fs.removeDirTree(service.path)

    def getTemplate(self,  name="", version="",domain="", role="", first=True, die=True):
        if first:
            return self.findTemplates(domain=domain, name=name, version=version, role=role, first=first)
        else:
            res = self.findTemplates(domain=domain, name=name, version=version, role=role, first=first)
            if len(res) > 1:
                if die:
                    j.events.inputerror_critical("Cannot get ays template '%s|%s (%s)', found more than 1" % (domain, name, version), "ays.gettemplate")
                else:
                    return
            if len(res) == 0:
                if die:
                    j.events.inputerror_critical("Cannot get ays template '%s|%s (%s)', did not find" % (domain, name, version), "ays.gettemplate")
                else:
                    return
            return res[0]

    def getRecipe(self, name="",version="", domain="", role=""):
        template = self.getTemplate(domain=domain,name=name, version=version, role=role)
        return template.recipe

    def getService(self,  role='', instance='main', die=True):
        """
        Return service indentifier by domain,name and instance
        throw error if service is not found or if more than one service is found
        """
        shortkey="%s!%s"%(role,instance)
        if shortkey in self.services:
            return self.services[shortkey]
        if die:
            j.events.inputerror_critical("Cannot get ays service '%s', did not find" % shortkey,"ays.getservice")
        else:
            return None

        return res[0]

    def loadServicesInSQL(self):
        """
        walk over all services and load into sqllite
        """
        from . import AYSdb

        def _loadHRDItems(hrddict, hrd, objectsql):
            hrds = list()
            recipes = list()
            processes = list()
            dependencies = list()
            for key, value in list(hrddict.items()):
                if key.startswith('service.process'):
                    continue
                elif key.startswith('process'):
                    processsql = AYSdb.Process()
                    if key == 'ports':
                        ports = list()
                        for port in value:
                            tcpportsql = AYSdb.TCPPort(tcpport=port)
                            sql.session.add(tcpportsql)
                            ports.append(tcpportsql)
                        processsql.ports = ports
                    elif key == 'env':
                        processsql.env = j.data.serializer.json.dumps(value)
                    else:
                        processsql.__setattr__(key, value)
                    sql.session.add(processsql)
                    processes.append(processsql)
                elif key.startswith('git.export') or key.startswith('service.web.export'):
                    recipesql = AYSdb.RecipeItem()
                    recipesql.order = key.split('export.', 1)[1]
                    recipesql.recipe = j.data.serializer.json.dumps(value)
                    sql.session.add(recipesql)
                    recipes.append(recipesql)
                elif key.startswith("service.dependencies") or key.startswith('dependencies'):
                    if not isinstance(value, list):
                        value = [value]
                    for val in value:
                        dependencysql = AYSdb.Dependency()
                        dependencysql.order = key.split('dependencies.', 1)[1] if key.startswith('dependencies.') else '1'
                        dependencysql.domain = val.get('domain', '')
                        dependencysql.name = val.get('name', '')
                        dependencysql.instance = val.get('instance', '')
                        dependencysql.args = j.data.serializer.json.dumps(val.get('args', '{}'))
                        sql.session.add(dependencysql)
                        dependencies.append(dependencysql)
                else:
                    hrdsql = AYSdb.HRDItem()
                    hrdsql.key = key
                    hrdsql.value = j.data.serializer.json.dumps(value)
                    hrdsql.isTemplate = True
                    sql.session.add(hrdsql)
                    hrds.append(hrdsql)

            objectsql.hrd = hrds
            objectsql.processes = processes
            objectsql.recipes = recipes
            objectsql.dependencies = dependencies

        sql = j.db.sqlalchemy.get(sqlitepath=j.dirs.varDir+"/AYS.db",tomlpath=None,connectionstring='')

        if not self._init:
            self._doinit()
        templates = self.findTemplates()
        services = self.findServices()

        attributes = ('domain', 'name', 'metapath')
        for template in templates:
            templatesql = AYSdb.Template()
            for attribute in attributes:
                templatesql.__setattr__(attribute, template.__getattribute__(attribute))

            instances = list()
            for instance in template.listInstances():
                instancesql = AYSdb.Instance(instance=instance)
                sql.session.add(instancesql)
                instances.append(instancesql)
            templatesql.instances = instances
            hrd = template.getHRD()
            hrddict = hrd.getHRDAsDict()

            _loadHRDItems(hrddict, hrd, templatesql)
            sql.session.add(templatesql)

        sql.session.commit()

        for service in services:
            servicesql = AYSdb.Service()
            attributes = ('domain', 'name', 'instance', 'parent', 'path', 'noremote', 'templatepath',
                          'cmd')
            for attribute in attributes:
                servicesql.__setattr__(attribute, service.__getattribute__(attribute))

            hrddict = service.hrd.getHRDAsDict()
            _loadHRDItems(hrddict, service.hrd, servicesql)

            servicesql.priority = service.getPriority()
            servicesql.logPath = service.getLogPath()
            servicesql.isInstalled = service.isInstalled()
            servicesql.isLatest = service.isLatest()

            producers = list()
            for key, value in list(service.producers.items()):
                producersql = AYSdb.Producer(key=key, value=value)
                sql.session.add(producersql)
                producers.append(producersql)
            servicesql.producer = producers

            categories = list()
            for category in service.categories:
                categorysql = AYSdb.Category(category=category)
                sql.session.add(categorysql)
                categories.append(categorysql)
            servicesql.category = categories

            processes = list()
            procs = getProcessDicts(hrd)
            for process in procs:
                processsql = AYSdb.Process()
                for key, value in list(process.items()):
                    if key == 'ports':
                        ports = list()
                        for port in value:
                            tcpportsql = AYSdb.TCPPort(tcpport=port)
                            sql.session.add(tcpportsql)
                            ports.append(tcpportsql)
                        processsql.ports = ports
                    elif key == 'env':
                        processsql.env = j.data.serializer.json.dumps(value)
                    else:
                        processsql.__setattr__(key, value)
                sql.session.add(processsql)
                processes.append(processsql)
            servicesql.processes = processes

            sql.session.add(servicesql)
        sql.session.commit()

    def getKey(self, service):
        """

        different formats
        - $domain|$name!$instance
        - $name
        - !$instance
        - $name!$instance

        version is added with ()
        - e.g. node.ssh (1.0)

        """
        key = service.name
        if service.domain != "":
            key = "%s|%s" % (service.domain, service.name)
        if hasattr(service, "instance") and service.instance is not None and service.instance != "":
            key += "!%s" % (service.instance)
        if service.version != "":
            key += " (%s)" % service.version
        return key.lower()

    def getServiceFromKey(self, key):
        """
        key in format $domain|$name!$instance@role ($version)

        different formats
        - $domain|$name!$instance
        - $name
        - !$instance
        - $name!$instance
        - @role

        version is added with ()
        - e.g. node.ssh (1.0)

        examples
        - find me service with role ns: '@ns' if more than 1 then there will be an error
        - find me a service with instance name ovh4 '!ovh4'

        """
        domain, name, version, instance, role = self.parseKey(key)
        return self.getService(instance=instance,role=role, die=True)

    def parseKey(self, key):
        """
        @return (domain,name,version,instance,role)

        """
        key = key.lower()
        if key.find("|") != -1:
            domain, name = key.split("|", 1)
        else:
            domain = ""
            name = key

        if key.find("@") != -1:
            name, role = key.split("@", 1)
            role = role.strip()
        else:
            role = ""

        if name.find("!") != -1:
            # found instance
            name, instance = name.split("!", 1)
            if instance.find("(") != -1:
                instance, version = instance.split("(", 1)
                name += "(%s" % version
            instance = instance.strip()
        else:
            instance = ""

        if name.find("(") != -1:
            name, version = name.split("(", 1)
            version = version.split(")", 1)[0]
        else:
            version = ""
        name = name.strip()
        domain = domain.strip()
        version = version.strip()
        return (domain, name, version, instance, role)

    def __str__(self):
        return self.__repr__()


    # def _getGitRepo(self, url, recipeitem=None, dest=None):
    #     if url in self._reposDone:
    #         return self._reposDone[url]

    #     login = None
    #     passwd = None
    #     if recipeitem is not None and "login" in recipeitem:
    #         login = recipeitem["login"]
    #         if login == "anonymous" or login.lower() == "none" or login == "" or login.lower() == "guest":
    #             login = "guest"
    #     if recipeitem is not None and "passwd" in recipeitem:
    #         passwd = recipeitem["passwd"]

    #     branch = None  # let branch be selected automatily
    #     if recipeitem is not None and "branch" in recipeitem:
    #         branch = recipeitem["branch"]

    #     revision = None
    #     if recipeitem is not None and "revision" in recipeitem:
    #         revision = recipeitem["revision"]

    #     depth = 1
    #     if recipeitem is not None and "depth" in recipeitem:
    #         depth = recipeitem["depth"]
    #         if isinstance(depth, str) and depth.lower() == "all":
    #             depth = None
    #         else:
    #             depth = int(depth)

    #     login = j.application.config.get("whoami.git.login").strip()
    #     passwd = j.application.config.getStr("whoami.git.passwd").strip()

    #     dest = j.do.pullGitRepo(url=url, login=login, passwd=passwd,
    #                             depth=depth, branch=branch, revision=revision, dest=dest)
    #     self._reposDone[url] = dest
    #     return dest
