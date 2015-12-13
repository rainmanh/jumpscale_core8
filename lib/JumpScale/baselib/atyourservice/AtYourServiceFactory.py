from JumpScale import j
from ServiceTemplate import ServiceTemplate
from Service import Service, getProcessDicts
import re
from ActionsBaseMgmt import ActionsBaseMgmt
from ActionsBaseTmpl import ActionsBaseTmpl
from ActionsBaseNode import ActionsBaseNode
from AtYourServiceDebug import AtYourServiceDebugFactory
# import AYSdb
import json
from AtYourServiceSync import AtYourServiceSync
import os


class AtYourServiceFactory():

    def __init__(self):
        self.__jslocation__ = "j.atyourservice"

        self._init = False
        self._domains = []
        self.hrd = None
        self._justinstalled = []
        self._type = None
        self.services = []
        self.templates = []
        self.indocker = False
        self.sync = AtYourServiceSync()
        self._reposDone = {}
        self.todo = []
        self._debug=None


    @property
    def debug(self):
        if self._debug==None:
            self._debug=AtYourServiceDebugFactory()
        return self._debug

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

            if self.type != "n":
                configpath=j.dirs.amInAYSRepo()
                # load service templates
                self._domains.append((j.sal.fs.getBaseName(configpath),"%s/servicetemplates/"%configpath))

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

    def _getRepo(self, url, recipeitem=None, dest=None):
        if url in self._reposDone:
            return self._reposDone[url]

        login = None
        passwd = None
        if recipeitem is not None and "login" in recipeitem:
            login = recipeitem["login"]
            if login == "anonymous" or login.lower() == "none" or login == "" or login.lower() == "guest":
                login = "guest"
        if recipeitem is not None and "passwd" in recipeitem:
            passwd = recipeitem["passwd"]

        branch = None  # let branch be selected automatily
        if recipeitem is not None and "branch" in recipeitem:
            branch = recipeitem["branch"]

        revision = None
        if recipeitem is not None and "revision" in recipeitem:
            revision = recipeitem["revision"]

        depth = 1
        if recipeitem is not None and "depth" in recipeitem:
            depth = recipeitem["depth"]
            if isinstance(depth, str) and depth.lower() == "all":
                depth = None
            else:
                depth = int(depth)

        login = j.application.config.get("whoami.git.login").strip()
        passwd = j.application.config.getStr("whoami.git.passwd").strip()

        dest = j.do.pullGitRepo(url=url, login=login, passwd=passwd,
                                depth=depth, branch=branch, revision=revision, dest=dest)
        self._reposDone[url] = dest
        return dest

    def updateTemplatesRepo(self, repos=[]):
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

    def getActionsBaseClassTmpl(self):
        return ActionsBaseTmpl

    def getActionsBaseClassNode(self):
        return ActionsBaseNode

    def getActionsBaseClassMgmt(self):
        return ActionsBaseMgmt

    def apply(self):
        self.check()
        if self.todo == []:
            self._findtodo()
        step = 1
        while self.todo != []:
            print("execute state changes, nr services to process: %s in step:%s" % (len(self.todo), step))
            for i in range(len(self.todo)):
                service = self.todo[i]
                service.install()

            self.todo = []
            step += 1
            self._findtodo()

    def check(self):
        for service in self.findServices():
            service.check()
        # for service in self.findServices():
        #     service.recurring.check()

    def applyprint(self):
        if self.todo == []:
            self._findtodo()
        step = 1
        print("execute state changes, nr services to process: %s in step:%s" % (len(self.todo), step))
        for i in range(len(self.todo)):
            service = self.todo[i]
            if service.state.changed():
                print("UPLOAD")
                service._uploadToNode()
                # service.state.installDoneOK()
                # j.sal.fs.copyFile("%s/instance.hrd"%service.path,"%s/instance_old.hrd"%service.path)
        self.todo = []
        step += 1
        self._findtodo()

    def _findtodo(self):
        for service in self.findServices():
            producersWaiting = service.getProducersWaitingApply(set())

            if len(producersWaiting)==0 and service.state.changed:
                print("%s waiting for install" % service)
                self.todo.append(service)
            # elif service in producersWaiting and len(producersWaiting)==1 and service.state.changed():
            # elif service.state.changed():
            #     print "%s waiting for install (mutual)" % service
            #     self.todo.append(service)
            elif j.application.debug:
                print("%s no change in producers" % service)

    def checkRevisions(self):
        if len(self.services) == 0:
            self.loadServices()

        for service in self.services:
            service.state.saveRevisions()

    def findTemplates(self, domain="", name="", version="", first=False, role=''):
        res = []
        self.loadTemplates()
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

    def loadServices(self, reload=False):
        if self.services == [] or reload:
            self._doinit()
            for instance_hrd_path in j.sal.fs.listFilesInDir(j.dirs.ays, recursive=True, \
                filter="instance.hrd", case_sensitivity='os', followSymlinks=True, listSymlinks=False):

                service_path = j.sal.fs.getDirName(instance_hrd_path)
                template_hrd_path = j.sal.fs.joinPaths(service_path, 'template.hrd')
                (domain, name, version, instance, role) = self.parseKey(j.sal.fs.getBaseName(service_path))

                hrd = j.data.hrd.get(instance_hrd_path, prefixWithName=False)

                parent = hrd.get("parent", "")

                service = Service(servicetemplate=template_hrd_path, instance=instance,path=service_path, args=None, parent=parent)

                self.services.append(service)

    def _loadTemplates(self, domain, path):
        for servicepath in j.sal.fs.listDirsInDir(path, recursive=False):
            dirname = j.do.getBaseName(servicepath)
            # print "dirname:%s"%dirname
            if not (dirname.startswith(".")):
                self._loadTemplates(domain,servicepath)
        # print path
        dirname = j.do.getBaseName(path)
        if dirname.startswith("_"):
            return
        if j.sal.fs.exists("%s/instance.hrd" % path) or j.sal.fs.exists("%s/service.hrd" % path) or j.sal.fs.exists("%s/actions.py" % path):
            templ = ServiceTemplate(path, domain=domain)
            self.templates.append(templ)

    def loadTemplates(self, domain="", path="", reload=False):
        if path == "":
            if self.templates == [] or reload:
                self._doinit()
                for domain, domainpath in self.domains:
                    # print "load template domain:%s"%domainpath
                    self._loadTemplates(domain, domainpath)
        else:
            self._loadTemplates(domain, path)
        return self.templates

    def findServices(self, name="", instance="", domain="", parent=None, version="", first=False, role="", node=None, include_disabled=False):
        self.loadServices()
        res = []

        for service in self.services:
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

    def new(self, domain="", name="", instance="main",path=None, parent=None, args={},version="",consume=""):
        """
        will create a new service from template

        @param args are the arguments which will overrule questions of the instance.hrd
        @param consume specifies which ays instances will be consumed
                format $role/$domain|$name!$instance,$role2/$domain2|$name2!$instance2

        """
        templ = self.findTemplates(domain, name,version,first=True)
        obj = templ.newInstance(instance=instance, path=path, parent=parent, args=args, consume=consume)
        return obj

    def remove(self, domain="", name="", instance="", role=""):
        for service in self.findServices(domain=domain, name=name, instance=instance, role=role):
            if service in self.services:
                self.services.remove(service)
            j.sal.fs.removeDirTree(service.path)

    def getTemplate(self, domain="", name="", version="", first=True, die=True):
        if first:
            return self.findTemplates(domain=domain, name=name, version=version, first=first)
        else:
            res = self.findTemplates(domain=domain, name=name, version=version, first=first)
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

    def getService(self, domain="", name="", version="", instance="", parent=None, first=False, role="", die=True, node=None, include_disabled=False):
        """
        Return service indentifier by domain,name and instance
        throw error if service is not found or if more than one service is found
        """
        res = self.findServices(domain=domain, name=name, instance=instance, version=version, parent=parent,
                                first=first, role=role, node=node, include_disabled=include_disabled)
        if first:
            return res
        else:
            if len(res) > 1:
                if die:
                    if role != "":
                        j.events.inputerror_critical("Cannot get ays service '%s|%s!%s@%s', found more than 1" % (domain, name, instance, role), "ays.getservice")
                    else:
                        j.events.inputerror_critical("Cannot get ays service '%s|%s!%s (%s)', found more than 1" % (domain, name, instance, version), "ays.getservice")
                else:
                    return None
            if len(res) == 0:
                if die:
                    if role != "":
                        j.events.inputerror_critical("Cannot get ays service '%s|%s!%s@%s', did not find" % (domain, name, instance, role), "ays.getservice")
                    else:
                        j.events.inputerror_critical("Cannot get ays service '%s|%s!%s (%s)', did not find" % (domain, name, instance, version), "ays.getservice")
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
                        processsql.env = json.dumps(value)
                    else:
                        processsql.__setattr__(key, value)
                    sql.session.add(processsql)
                    processes.append(processsql)
                elif key.startswith('git.export') or key.startswith('service.web.export'):
                    recipesql = AYSdb.RecipeItem()
                    recipesql.order = key.split('export.', 1)[1]
                    recipesql.recipe = json.dumps(value)
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
                        dependencysql.args = json.dumps(val.get('args', '{}'))
                        sql.session.add(dependencysql)
                        dependencies.append(dependencysql)
                else:
                    hrdsql = AYSdb.HRDItem()
                    hrdsql.key = key
                    hrdsql.value = json.dumps(value)
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
                        processsql.env = json.dumps(value)
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

    def getServiceFromKey(self, key, node=None, die=True, include_disabled=False):
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
        return self.getService(domain=domain, name=name, instance=instance, version=version,
                               role=role, die=die, node=node, include_disabled=include_disabled)

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
