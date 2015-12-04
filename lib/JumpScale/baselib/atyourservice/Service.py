from JumpScale import j
import JumpScale.baselib.actions
# import JumpScale.baselib.packInCode
# 
from collections import OrderedDict

# import pytoml
import json
import imp
import sys
from functools import wraps
from .ServiceState import *
from .Recurring import Recurring

def log(msg, level=2):
    j.logger.log(msg, level=level, category='AYS')

def loadmodule(name, path):
    parentname = ".".join(name.split(".")[:-1])
    sys.modules[parentname] = __package__
    mod = imp.load_source(name, path)
    return mod


def getProcessDicts(hrd, args={}):
    counter = 0

    defaults = {"prio": 10, "timeout_start": 10,
                "timeout_start": 10, "startupmanager": "tmux"}
    musthave = ["cmd", "args", "prio", "env", "cwd", "timeout_start",
                "timeout_start", "ports", "startupmanager", "filterstr", "name", "user"]

    procs = hrd.getListFromPrefixEachItemDict("process", musthave=musthave, defaults=defaults, aredict=[
                                                   'env'], arelist=["ports"], areint=["prio", "timeout_start", "timeout_start"])
    for process in procs:
        counter += 1

        process["test"] = 1

        if process["name"].strip() == "":
            process["name"] = "%s_%s" % (
                hrd.get("name"), hrd.get("instance"))

        if hrd.exists("env.process.%s" % counter):
            process["env"] = hrd.getDict("env.process.%s" % counter)

        if not isinstance(process["env"], dict):
            raise RuntimeError("process env needs to be dict")

    return procs


class Service(object):

    def __init__(self, servicetemplate=None, instance="main", path="", args=None, parent=None, originator=None):
        """
        @param consume is in format $role/$domain|$name!$instance,$role2/$name2!$instance2,$role3/$name2,$role4
        """
        self.originator = originator

        # self.processed = dict()
        if j.core.types.string.check(servicetemplate):
            # load from existing instance, get template data from template.hrd
            tmpl_hrd = j.core.hrd.get(servicetemplate, prefixWithName=False)
            self.name = tmpl_hrd.getStr('name').lower()
            self.version = tmpl_hrd.getStr('version')
            self.domain = tmpl_hrd.getStr('domain').lower()
            self._servicetemplate = None
        else:
            # new service, load template data from template object
            if servicetemplate is None:
                raise RuntimeError("servicetemplate should not be none")

            self.name = servicetemplate.name.lower()
            self.version = servicetemplate.version
            self.domain = servicetemplate.domain.lower()
            self._servicetemplate = servicetemplate

        self.instance = instance.lower()

        self._parentkey = None
        self._parent = None
        self._parentChain = None

        self.role = self.name.split(".")[0]

        self.path = path.rstrip("/")

        self._hrd = None
        self._hrd_template = None
        self._actions_mgmt = None
        self._actions_node = None
        self._actions_tmpl = None

        self._dnsNames = []

        if parent is not None and parent != "":
            if j.core.types.string.check(parent):
                self._parentkey = parent
                self._parent = None
            else:
                self._parentkey = parent.key
                self._parent = parent

        if self._parentkey is None:
            self._parentkey = ""

        self.args = args or {}
        self._producers = {}
        self.cmd = None
        self._logPath = None

        if self.path == "" or self.path is None:
            raise RuntimeError("cannot be empty")

        self._init = False

        self._state = ServiceState(self)

        self._executor = None

        self._recurring = None

    @property
    def key(self):
        return j.atyourservice.getKey(self)


    @property
    def template(self):
        if self._servicetemplate is not None:
            return self._servicetemplate

        return j.atyourservice.getTemplate(domain=self.domain, name=self.name, version=self.version)
        # servicetemplates = j.atyourservice.findTemplates(domain=self.domain, name=self.name, version=self.version)
        # if len(servicetemplates) == 0:
        #     j.events.opserror_critical(msg="cannot find service template for : %s__%s (%s)" % (self.domain, self.name, self.version), category="ays.service")
        # elif len(servicetemplates) > 1:
        #     j.events.opserror_critical(msg="found too many templates for : %s__%s (%s)" % (self.domain, self.name, self.version), category="ays.service")

        # servicetemplate = servicetemplates[0]
        # self._servicetemplate = servicetemplate
        # return servicetemplate

    @property
    def dnsNames(self):
        if self._dnsNames == []:
            self._dnsNames = self.hrd.getList("dns")
        return self._dnsNames

    @property
    def parents(self):
        if self._parentChain is not None:
            return self._parentChain
        chain = []
        parent = self.parent
        while parent is not None:
            chain.append(parent)
            parent = parent.parent
        self._parentChain = chain
        return chain

    @property
    def parent(self):
        if self._parent is not None:
            return self._parent
        if self._parentkey != "":
            self._parent = j.atyourservice.getServiceFromKey(self._parentkey)
            return self._parent

    @property
    def hrd(self):
        if self._hrd:
            return self._hrd
        hrdpath = j.system.fs.joinPaths(self.path, "instance.hrd")
        if not j.system.fs.exists(hrdpath):
            self._apply()
        else:
            self._hrd = j.core.hrd.get(hrdpath, prefixWithName=False)
        return self._hrd

    @property
    def hrd_template(self):
        if self._hrd_template:
            return self._hrd_template
        path = j.system.fs.joinPaths(self.path, "template.hrd")
        self._hrd_template = j.core.hrd.get(path, prefixWithName=False)
        return self._hrd_template

    @property
    def state(self):
        if self._state:
            return self._state
        self._state = ServiceState(self)
        if self._state.checkChangeState():
            self._state.saveState()
        return self._state

    @property
    def actions_tmpl(self):
        if self._actions_tmpl is None:
            path = j.system.fs.joinPaths(self.path, "actions_tmpl.py")
            if j.system.fs.exists(path=path):
                self._actions_tmpl = self._loadActions(path)
            else:
                self._actions_tmpl = j.atyourservice.getActionsBaseClassTmpl()()

        return self._actions_tmpl

    @property
    def actions_mgmt(self):
        if self._actions_mgmt is None:
            path = j.system.fs.joinPaths(self.path, "actions_mgmt.py")
            if j.system.fs.exists(path=path):
                self._actions_mgmt = self._loadActions(path)
            else:
                self._actions_mgmt = j.atyourservice.getActionsBaseClassMgmt()()

        return self._actions_mgmt

    @property
    def actions_node(self):
        if self._actions_node is None:
            path = j.system.fs.joinPaths(self.path, "actions_node.py")
            if j.system.fs.exists(path=path):
                self._actions_node = self._loadActions(path)
            else:
                self._actions_node = j.atyourservice.getActionsBaseClassNode()()

        return self._actions_node

    @property
    def producers(self):
        if self._producers != {}:
            return self._producers

        for key, items in self.hrd.getDictFromPrefix("producer").items():
            producerSet = set()
            for item in items:
                service = j.atyourservice.getServiceFromKey(item.strip())
                producerSet.add(service)

            self._producers[key] = list(producerSet)

        return self._producers

    @property
    def logPath(self):
        if self._logPath is None:
            self._logPath = j.system.fs.joinPaths(self.path, "log.txt")
        return self._logPath

    @property
    def executor(self):
        if self._executor is None:
            self._executor = self._getExecutor()
        return self._executor

    @property
    def recurring(self):
        if self._recurring is None:
            self._recurring = Recurring(self)
        return self._recurring

    def _loadActions(self, path):
        if j.system.fs.exists(path+'c'):
            j.system.fs.remove(path+'c')
        if j.system.fs.exists(path):
            if self._hrd is not None:
                self.hrd.applyOnFile(path)
            j.application.config.applyOnFile(path)
        else:
            j.events.opserror_critical(msg="can't find %s." % path, category="ays loadActions")

        modulename = "JumpScale.atyourservice.%s.%s.%s" % (self.domain, self.name, self.instance)
        mod = loadmodule(modulename, path)
        return mod.Actions()

    def init(self):
        if self._init is False:
            self._apply()
        self._init = True

    def consume(self, input):
        """
        @input is comma separate list of ayskeys or a ays object

        ayskeys in format $domain|$name:$instance@role ($version)

        example
        ```
        @input $domain|$name!$instance,$name2!$instance2,$name2,$role4
        ```

        """

        if str(input).strip() == "":
            return

        emsg = "consume format is: ayskey,ayskey"
        print("consume from %s:%s" % (self, input))
        if input is not None and input is not '':

            # if hasattr(input, "name"):
            if isinstance(input, Service):
                # is a service object
                service = input
                if service.role not in self._producers:
                    self._producers[service.role] = [service]
                else:
                    prodSet = set(self._producers[service.role])
                    prodSet.add(service)
                    self._producers[service.role] = list(prodSet)
            else:
                entities = input.split(",")
                for entry in entities:
                    print("get service for consumption:%s" % entry.strip())
                    service = j.atyourservice.getServiceFromKey(entry.strip())
                    if service.role not in self._producers:
                        self._producers[service.role] = [service]
                    else:
                        prodSet = set(self._producers[service.role])
                        prodSet.add(service)
                        self._producers[service.role] = list(prodSet)

            for key, services in self._producers.items():
                producers = []
                for service in services:
                    key0 = j.atyourservice.getKey(service)
                    if key0 not in producers:
                        producers.append(key0)

            if self._hrd is not None:
                self.hrd.set("producer.%s" % key, producers)

        print("consumption done")

    def check(self):
        """
        check if template file changed with local
        """
        self._apply()
        if self.state.changed():
            if self.state.hrd.getBool("hrd.instance.changed"):
                print("%s hrd.instance.changed" % self)
            if self.state.hrd.getBool("hrd.template.changed"):
                print("%s hrd.template.changed" % self)
            if self.state.hrd.getBool("actions.changed"):
                print("%s actions.changed" % self)

    def getProducersRecursive(self, producers=set(), callers=set()):
        for role, producers2 in self.producers.items():
            for producer in producers2:
                producers.add(producer)
                producers = producer.getProducersRecursive(producers, callers=callers)
        return producers.symmetric_difference(callers)

    def getProducersWaitingApply(self, producersChanged=set()):
        """
        return list of producers which are waiting to be deployed
        """
        for producer in self.getProducersRecursive(set(), set()):
                if producer.state.changed():
                    producersChanged.add(producer)
        return producersChanged

    def getNode(self):
        for parent in self.parents:
            if 'node' == parent.role:
                return parent
        return None

    def isOnNode(self,node=None):
        mynode = self.getNode()
        if mynode is None:
            return False
        return mynode.key == node.key

    def isInstalled(self):
        #@todo lets first debug like this and then later do the rest
        #will be use the ServiceState (kds will do this, first everything else needs to work again)
        return False

    # def isLatest(self):
    #     #@todo lets first debug like this and then later do the rest
    #     return False

    #     #@todo rework
    #     from IPython import embed
    #     print "DEBUG NOW isLatest"
    #     embed()

    #     if not self.isInstalled():
    #         return False
    #     checksum = self.hrd.get('service.installed.checksum')
    #     checksumpath = j.system.fs.joinPaths(self.path, "installed.version")
    #     #@todo how can this ever be different, doesn't make sense to me? (despiegk)
    #     installedchecksum = j.system.fs.fileGetContents(checksumpath).strip()
    #     if checksum != installedchecksum:
    #         return False
    #     for recipeitem in self.hrd.getListFromPrefix("git.export"):
    #         if not recipeitem:
    #             continue
    #         branch = recipeitem.get('branch', 'master') or 'master'
    #         recipeurl = recipeitem['url']
    #         if recipeurl in self._reposDone:
    #             continue

    #         login = j.application.config.get("whoami.git.login").strip()
    #         passwd = j.application.config.getStr("whoami.git.passwd").strip()
    #         _, _, _, _, dest, url = j.do.getGitRepoArgs(
    #             recipeurl, login=login, passwd=passwd)

    #         current = j.system.process.execute(
    #             'cd %s; git rev-parse HEAD --branch %s' % (dest, branch))
    #         current = current[1].split('--branch')[1].strip()
    #         remote = j.system.process.execute(
    #             'git ls-remote %s refs/heads/%s' % (url, branch))
    #         remote = remote[1].split()[0]

    #         if current != remote:
    #             return False
    #         self._reposDone[recipeurl] = dest
    #     return True

    def getTCPPorts(self, processes=None, *args, **kwargs):
        ports = set()
        if processes is None:
            processes = self.getProcessDicts()
        for process in self.getProcessDicts():
            for item in process.get("ports", []):
                if isinstance(item, str):
                    moreports = item.split(";")
                elif isinstance(item, int):
                    moreports = [item]
                for port in moreports:
                    if isinstance(port, int) or port.isdigit():
                        ports.add(int(port))
        return list(ports)

    def getPriority(self):
        processes = self.getProcessDicts()
        if processes:
            return processes[0].get('prio', 100)
        return 199

    def getProcessDicts(self, args={}):
        return getProcessDicts(self.hrd_template, args={})

    # def getDependencyChain(self, chain=None):
    #     chain = chain if chain is not None else []
    #     dependencies = self.getDependencies()
    #     for dep in dependencies:
    #         dep.getDependencyChain(chain)
    #         if self in chain:
    #             if dep not in chain:
    #                 chain.insert(chain.index(self)+1, dep)
    #             if dep in chain and chain.index(dep) > chain.index(self):
    #                 dependant = chain.pop(self)
    #                 chain.insert(chain.index(dep), dependant)
    #         else:
    #             if dep not in chain:
    #                 chain.append(dep)
    #     return chain

    def _apply(self):
        # log("apply")
        j.do.createDir(self.path)

        # make sure they are loaded (properties), otherwise paths will be wrong
        self.template.actions
        self.template.hrd_template
        self.template.hrd_instance

        items = ["actions_mgmt", "actions_node", "actions_tmpl"]
        for item in items:
            source = "%s/%s.py" % (self.template.path,item)
            if j.system.fs.exists(source):
                j.do.copyFile(source,  j.system.fs.joinPaths(self.path, "%s.py" % item))

        source = self.template.path_hrd_template
        j.do.copyFile(source, "%s/template.hrd" % self.path)

        path_templatehrd = "%s/template.hrd" % self.path
        tmpl_hrd = j.core.hrd.get(path_templatehrd, prefixWithName=False)

        tmpl_hrd.set('domain', self.domain)
        tmpl_hrd.set('name', self.name)
        tmpl_hrd.set('version', self.version)
        tmpl_hrd.set('instance', self.instance)
        tmpl_hrd.process()  # force replacement of $() inside the file itself

        path_instancehrd_new="%s/instance.hrd" % self.path
        path_instancehrd_old="%s/instance_old.hrd" % self.path

        # print path_instancehrd_old
        if not j.system.fs.exists(path=path_instancehrd_new):
            path_instancehrd = "%s/instance_.hrd" % self.path
            source = self.template.path_hrd_instance
            j.do.copyFile(source, path_instancehrd)

            hrd = j.core.hrd.get(path_instancehrd, prefixWithName=False)
            args0 = {}
            for key, item in self.template.hrd_instance.items.items():
                if item.data.startswith("@ASK"):
                    args0[key] = item.data
                else:
                    args0[key] = item.get()
            args0.update(self.args)

            # here the args can be manipulated
            if self.actions_mgmt != None:
                self.actions_mgmt.init(self, args0)
            self._actions_mgmt = None  # force to reload later with new value of hrd

            hrd.setArgs(args0)

            for key,item in hrd.items.items():
                if j.core.types.string.check(item.data) and item.data.find("@ASK") != -1:
                    item.get() #SHOULD DO THE ASK

            producers0={}
            for key, services in self._producers.items():#hrdnew.getDictFromPrefix("producer").iteritems():
            #     producers0[key]=[j.atyourservice.getServiceFromKey(item.strip()) for item in item.split(",")]

            # for role,services in producers0.iteritems():
                producers=[]
                for service in services:
                    key0=j.atyourservice.getKey(service)
                    if key0 not in producers:
                        producers.append(key0)
                hrd.set("producer.%s"%key,producers)

            if self.parent or self._parentkey != '':
                hrd.set('parent', self._parentkey)

            j.application.config.applyOnFile(path_instancehrd)
            hrd.applyOnFile(path_templatehrd)
            hrd.save()

            j.system.fs.moveFile(path_instancehrd,path_instancehrd_new)
            path_instancehrd=path_instancehrd_new

            hrd.path=path_instancehrd

        else:
            hrd=j.core.hrd.get(path_instancehrd_new)
            path_instancehrd=path_instancehrd_new

        hrd.applyOnFile(path_templatehrd)
        j.application.config.applyOnFile(path_templatehrd)
        tmpl_hrd = j.core.hrd.get(path_templatehrd, prefixWithName=False)

        actionPy = j.system.fs.joinPaths(self.path, "actions_mgmt.py")
        if j.system.fs.exists(path=actionPy):
            hrd.applyOnFile(actionPy) #@todo somewhere hrd gets saved when doing apply (WHY???)
            tmpl_hrd.applyOnFile(actionPy)
            j.application.config.applyOnFile(actionPy)
        actionPy = j.system.fs.joinPaths(self.path, "actions_node.py")
        if j.system.fs.exists(path=actionPy):
            hrd.applyOnFile(actionPy) #@todo somewhere hrd gets saved when doing apply (WHY???)
            tmpl_hrd.applyOnFile(actionPy)
            j.application.config.applyOnFile(actionPy)

        self._state=ServiceState(self)

        # not sure this code is this code is still relevent here, cause the _apply()
        # method is now only called once at service init.
        change=self.state.checkChangeState()

        if change:
            #found changes in hrd or one of the actionfiles
            oldhrd_exists=j.system.fs.exists(path=path_instancehrd_old)
            if not oldhrd_exists:
                j.do.writeFile(path_instancehrd_old,"")

            hrdold=j.core.hrd.get(path_instancehrd_old)

            self.state.commitHRDChange(hrdold,hrd)

            # if not oldhrd_exists:
            #     #we don't want to overwrite the oldest known copy of the hrd
            #     if j.system.fs.exists(path=hrdpathnew):
            #         #can be there is not service.hrd yet
            #         j.do.copyFile(hrdpathnew, hrdpathold)

        self._hrd=hrd

        if self.state.changed:
            self.state.saveState()

    def _uploadToNode(self):
        # ONLY UPLOAD THE SERVICE ITSELF, INIT NEEDS TO BE FIRST STEP, NO IMMEDIATE INSTALL
        if "node" not in self.producers:
            return
        hrd_root = "/etc/ays/local/"
        remotePath = j.system.fs.joinPaths(hrd_root, j.system.fs.getBaseName(self.path)).rstrip("/")+"/"
        print("uploading %s '%s'->'%s'" % (self.key,self.path,remotePath))
        self.executor.upload(self.path, remotePath,recursive=False)


    def _downloadFromNode(self):
        if 'node' not in self.producers or self.executor is None:
            return

        hrd_root = "/etc/ays/local/"
        remotePath = j.system.fs.joinPaths(hrd_root, j.system.fs.getBaseName(self.path), 'instance.hrd')
        dest = self.path.rstrip("/")+"/"+"instance.hrd"
        print("downloading %s '%s'->'%s'" % (self.key, remotePath, self.path))
        self.executor.download(remotePath, self.path)

    def _getExecutor(self):
        if 'node' in self.producers and len(self.producers["node"]) > 1:
            raise RuntimeError("found more then 1 executor for %s" % self)

        executor = None
        if 'node' in self.producers and self.producers.get('node'):
            node = self.producers["node"][0]
            if '"agentcontroller2' in node.producers:
                # this means an agentcontroller is responsible for the node which hosts this service
                agentcontroller = node.producers["agentcontroller2"][0]
                # make more robust
                agent2controller2client = agentcontroller.producers["agent2controller2client"][0]
                executor = j.tools.executor.getJSAgent2Based(agent2controller2client.key)
            elif node.hrd.exists("node.tcp.addr") and node.hrd.exists("ssh.port"):
                # is ssh node
                executor = j.tools.executor.getSSHBased(node.hrd.get("node.tcp.addr"), node.hrd.get("ssh.port"))
            else:
                executor = j.tools.executor.getLocal()
        else:
            executor = j.tools.executor.getLocal()

        if executor is None:
            raise RuntimeError("cannot find executor")

        return executor


    def log(self, msg):
        logpath = j.system.fs.joinPaths(self.path, "log.txt")
        if not j.system.fs.exists(self.path):
            j.system.fs.createDir(self.path)
        msg = "%s : %s\n" % (
            j.base.time.formatTime(j.base.time.getTimeEpoch()), msg)
        j.system.fs.writeFile(logpath, msg, append=True)

    def listChildren(self):
        childDirs = j.system.fs.listDirsInDir(self.path)
        childs = {}
        for path in childDirs:
            child = j.system.fs.getBaseName(path)
            ss = child.split("__")
            name = ss[0]
            instance = ss[1]
            if name not in childs:
                childs[name] = []
            childs[name].append(instance)
        return childs

    # def _consume(self, producerservice, producercategory):
    #     """
    #     create connection between consumer (this service) & producer
    #     producer category is category of service
    #     @param producerservice is serviceObj or servicekey
    #     """
    #     if j.core.types.string.check(producerservice):
    #         producerservice = j.atyourservice.getServiceFromKey(producerservice)
    #     key = "producer.%s" % producercategory
    #     val = self.hrd.get(key, "").strip().strip("'").strip()
    #     if val.find(producerservice.key) == -1:
    #         if val != "":
    #             val = "%s,%s" % (val, producerservice.key)
    #         else:
    #             val = "%s" % producerservice.key
    #         self.hrd.set(key, val)

    #         self.init()

    def getProducers(self, producercategory):
        if producercategory not in self.producers:
            j.events.inputerror_warning("cannot find producer with category:%s"%producercategory,"ays.getProducer")
        instances = self.producers[producercategory]
        return instances

    def __eq__(self, service):
        if not service:
            return False
        return service.name == self.name and self.domain == service.domain and self.instance == service.instance

    def __hash__(self):
      return hash((self.domain, self.name, self.instance, self.role, self.version))

    def __repr__(self):
        return '%s|%s!%s(%s)' % (self.domain, self.name, self.instance, self.version)

    def __str__(self):
        return self.__repr__()

    # ACTIONS
    def _executeOnNode(self, actionName, cmd=None, reinstall=False):
        if 'node' not in self.producers or self.executor is None:
            return False

        cmd2 = ' -d %s -n %s -i %s' % (self.domain, self.name, self.instance)
        execCmd = 'aysexec -a %s %s' % (actionName, cmd2)

        executor = self.executor
        executor.execute(execCmd, die=True)

        return True

    def stop(self):
        self.log("stop instance")
        self._executeOnNode("stop")
        self.recurring.stop()
        self.actions_mgmt.stop(self)

        if not self.actions_mgmt.check_down(self):
            self.actions_mgmt.halt(self)
            self._executeOnNode("halt")

    def start(self):
        self.log("start instance")
        self._executeOnNode("start")
        self.recurring.start()
        self.actions_mgmt.start(self)

    def restart(self):
        self.stop()
        self.start()

    def prepare(self):
        self._executeOnNode("prepare")

    def install(self, start=True):
        """
        Install Service.

        Keyword arguments:
        start     -- whether Service should start after install (default True)
        reinstall -- reinstall if already installed (default False)
        """

        log("INSTALL:%s" % self)
        # do the consume
        for key, producers in self.producers.items():
            for producer in producers:
                self.actions_mgmt.consume(self, producer)
        self._apply()

        if self.state.changed():
            self._uploadToNode()

        self._executeOnNode('install')

        self.stop()
        self.prepare()

        # self._install()
        self.configure()

        # now we can remove changes of statefile & remove old hrd
        self.state.installDoneOK()
        j.system.fs.copyFile(
            j.system.fs.joinPaths(self.path, "instance.hrd"),
            j.system.fs.joinPaths(self.path, "instance_old.hrd")
        )

        if start:
            self.start()

        if self.template.hrd_template.getBool("hrd.return", False):
            self._downloadFromNode()
            # need to reload the downloaded instance.hrd file
            self._hrd = j.core.hrd.get(j.system.fs.joinPaths(self.path, 'instance.hrd'), prefixWithName=False)


    def _getDisabledProducers(self):
        producers = dict()
        for key, items in self.hrd.getDictFromPrefix("producer").items():
            producers[key] = [j.atyourservice.getServiceFromKey(item.strip(), include_disabled=True) for item in items]
        return producers

    def _getConsumers(self, include_disabled=False):
        consumers = list()
        services = j.atyourservice.findServices(include_disabled=True, first=False)
        for service in services:
            producers = service._getDisabledProducers() if include_disabled else service.producers
            if self.role in producers and self in producers[self.role]:
                consumers.append(service)
        return consumers

    def disable(self):
        self.stop()
        for consumer in self._getConsumers():
            candidates = j.atyourservice.findServices(role=self.role, first=False)
            if len(candidates) > 1:
                # Other candidates available. Should link consumer to new candidate
                candidates.remove(self)
                candidate = candidates[0]
                producers = consumer.hrd.getList('producer.%s' % self.role, [])
                producers.remove(self.key)
                producers.append(candidate.key)
                consumer.hrd.set('producer.%s' % self.role, producers)
            else:
                # No other candidates already installed. Disable consumer as well.
                consumer.disable()

        self.log("disable instance")
        self.state.hrd.set('disabled', True)

    def _canBeEnabled(self):
        for role, producers in list(self.producers.items()):
            for producer in producers:
                if producer.state.hrd.getBool('disabled', False):
                    return False
        return True

    def enable(self):
        # Check that all dependencies are enabled

        if not self._canBeEnabled():
            print("%s cannot be enabled because one or more of its producers is disabled" % self)
            return

        self.state.hrd.set('disabled', False)
        self.log("Enable instance")
        for consumer in self._getConsumers(include_disabled=True):
            consumer.enable()
            consumer.start()

    # def _install(self, reinstall=False):


        # self.configure()

    def publish(self):
        """
        check which repo's are used & push the info
        this does not use the build repo's
        """
        if self._executeOnNode("publish"):
            return

        self.log("publish instance")
        self.actions_mgmt.publish(self)

    def package(self):
        """
        """
        if self._executeOnNode("package"):
            return

        self.actions_mgmt.package(self)


    def update(self):
        """
        - go over all related repo's & do an update
        - copy the files again
        - restart the app
        """
        if self._executeOnNode("update"):
            return

        self.log("update instance")
        for recipeitem in self.hrd.getListFromPrefix("git.export"):
            # pull the required repo
            j.atyourservice._getRepo(recipeitem['url'], recipeitem=recipeitem)

        for recipeitem in self.hrd.getListFromPrefix("git.build"):
            # print recipeitem
            # pull the required repo
            name = recipeitem['url'].replace(
                "https://", "").replace("http://", "").replace(".git", "")
            dest = "/opt/build/%s/%s" % name
            j.do.pullGitRepo(dest=dest, ignorelocalchanges=True)

        self.restart()

    def resetstate(self):
        """
        remove state of a service.
        """
        raise RuntimeError("not implemented")
        if self._executeOnNode("resetstate"):
            return

        statePath = j.system.fs.joinPaths(self.path, 'state.toml')
        j.do.delete(statePath)

    def reset(self):
        """
        - remove build repo's !!!
        - remove state of the app (same as resetstate) in jumpscale (the configuration info)
        - remove data of the app
        """
        if self._executeOnNode("reset"):
            return

        self.log("reset instance")
        # remove build repo's
        for recipeitem in self.hrd.getListFromPrefix("git.build"):
            name = recipeitem['url'].replace(
                "https://", "").replace("http://", "").replace(".git", "")
            dest = "/opt/build/%s" % name
            j.do.delete(dest)

        self.actions_mgmt.removedata(self)
        j.atyourservice.remove(self)

    def removedata(self):
        """
        - remove build repo's !!!
        - remove state of the app (same as resetstate) in jumpscale (the configuration info)
        - remove data of the app
        """
        self._executeOnNode("removedata")

        self.log("removedata instance")
        self.actions_mgmt.removedata(self)

    def execute(self, cmd=None):
        """
        execute cmd on service
        """
        if self._executeOnNode("execute", cmd=cmd):
            return

        if cmd is None:
            cmd = self.cmd
        self.actions_mgmt.execute(self, cmd=cmd)

    def _uninstall(self):
        for recipeitem in self.hrd_template.getListFromPrefix("web.export"):
            if "dest" not in recipeitem:
                raise RuntimeError("could not find dest in hrditem for %s %s" % (recipeitem, self))
            dest = recipeitem['dest']
            j.system.fs.removeDirTree(dest)

        for recipeitem in self.hrd_template.getListFromPrefix("git.export"):
            if "platform" in recipeitem:
                if not j.system.platformtype.checkMatch(recipeitem["platform"]):
                    continue

            if "link" in recipeitem and str(recipeitem["link"]).lower() == 'true':
                # means we need to only list files & one by one link them
                link = True
            else:
                link = False

            repository_type, repository_account, repository_name = recipeitem['url'].strip('http://').strip('https://').split('/', 3) #'http://git.aydo.com/binary/mongodb',
            repository_type = repository_type.split('.')[0]
            srcdir = '%(codedir)s/%(type)s/%(account)s/%(repo_name)s' % {
                'codedir': j.dirs.codeDir,
                'type': repository_type.lower(),
                'account': repository_account.lower(),
                'repo_name': repository_name,
            }

            src = recipeitem['source']
            src = j.system.fs.joinPaths(srcdir, src)

            if "dest" not in recipeitem:
                raise RuntimeError(
                    "could not find dest in hrditem for %s %s" % (recipeitem, self))
            dest = recipeitem['dest']

            if src[-1] == "*":
                src = src.replace("*", "")
                if "nodirs" in recipeitem and str(recipeitem["nodirs"]).lower() == 'true':
                    # means we need to only list files & one by one link them
                    nodirs = True
                else:
                    nodirs = False

                items = j.do.listFilesInDir(
                    path=src, recursive=False, followSymlinks=False, listSymlinks=False)
                if nodirs is False:
                    items += j.do.listDirsInDir(
                        path=src, recursive=False, dirNameOnly=False, findDirectorySymlinks=False)

                items = [(item, "%s/%s" % (dest, j.do.getBaseName(item)), link)
                         for item in items]
            else:
                items = [(src, dest, link)]

            for src, dest, link in items:
                if dest.strip() == "":
                    raise RuntimeError("a dest in coderecipe cannot be empty for %s" % self)
                if dest[0] != "/":
                    dest = "/%s" % dest
                else:
                    if link:
                        if j.system.fs.exists(dest):
                            j.system.fs.unlink(dest)
                    else:
                        print(("deleting: %s" % dest))
                        j.system.fs.removeDirTree(dest)

    def uninstall(self):
        self._executeOnNode("uninstall")


        self.log("uninstall instance")
        self.disable()
        self._uninstall()
        self.actions_mgmt.uninstall(self)
        j.system.fs.removeDirTree(self.path)

    def monitor(self):
        """
        Schedule the monitor local and monitor remote methods
        """
        if self._executeOnNode("monitor"):
            res = self.actions_mgmt.check_up_local(self)
            res = res and self.actions_mgmt.schedule_monitor_local(self)
            res = res and self.actions_mgmt.schedule_monitor_remote(self)
            return res

        return True

    def iimport(self, url):
        if self._executeOnNode("import"):
            return

        self.log("import instance data")
        self.actions_mgmt.data_import(url, self)

    def export(self, url):
        if self._executeOnNode("export"):
            return

        self.log("export instance data")
        self.actions.data_export(url, self)

    def configure(self, restart=True):
        self._executeOnNode("configure")

        self.log("configure instance")
        res = self.actions_mgmt.configure(self)
        if res is False:
            j.events.opserror_critical(msg="Could not configure %s" % self, category="ays.service.configure")
        if res == "r":
            restart = True
        if res == 'nr':
            retart = False
        if restart:
            self.restart()
