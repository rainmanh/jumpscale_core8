from JumpScale import j
# import JumpScale.baselib.actions

# import pytoml
# from contextlib import redirect_stdout
import io
import imp
import sys
from functools import wraps
from Recurring import Recurring

# def log(msg, level=2):
#     j.logger.log(msg, level=level, category='AYS')

def loadmodule(name, path):
    parentname = ".".join(name.split(".")[:-1])
    sys.modules[parentname] = __package__
    mod = imp.load_source(name, path)
    return mod

def getProcessDicts(service, args={}):
    counter = 0

    defaults = {"prio": 10, "timeout_start": 10,
                "timeout_start": 10, "startupmanager": "tmux"}
    musthave = ["cmd", "args", "prio", "env", "cwd", "timeout_start",
                "timeout_start", "ports", "startupmanager", "filterstr", "name", "user"]

    procs = service.recipe.hrd.getListFromPrefixEachItemDict("process", musthave=musthave, defaults=defaults, aredict=[
                                                   'env'], arelist=["ports"], areint=["prio", "timeout_start", "timeout_start"])
    for process in procs:
        counter += 1

        process["test"] = 1

        if "name" not in process or process["name"].strip() == "":
            process["name"] = "%s_%s" % (service.name, service.instance)

        if service.recipe.hrd.exists("env.process.%s" % counter):
            process["env"] = service.recipe.hrd.getDict("env.process.%s" % counter)

        if not isinstance(process["env"], dict):
            raise RuntimeError("process env needs to be dict")

    return procs

class ActionRun():

    def __init__(self,service,name,epoch=0,state="",printonly=False):
        """
        @param state: INIT, START, OK, ERROR
        """
        self.service=service
        self.name=name
        self._method_node=""
        self._method_mgmt_pre=""
        self._method_mgmt_post=""
        self._method_mgmt=""
        self._methods=""
        self.epoch=epoch
        if self.epoch==0:
            self.epoch=j.data.time.getTimeEpoch()
        self._state=state
        self.printonly=printonly
        if self.state=="":
            raise RuntimeError("state cannot be empty")

    def setState(self,state):
        if state !=self.state:
            j.atyourservice.alog.newAction(self.service,self.name,state=state,logonly=True)
            self._state=state

    @property
    def state(self):
        return self._state


    @property
    def method_node(self):
        if self._method_node == "":
            if self.service.parent != None:
                if self.service.parent.role == "ssh":
                    self._method_node = self.service._getActionMethodNode(self.name)
                    return self._method_node
            self._method_node=None
        return self._method_node

    @property
    def method_mgmt(self):
        if self._method_mgmt=="":
            self._method_mgmt=self.service._getActionMethodMgmt(self.name)
        return self._method_mgmt

    @property
    def method_mgmt_pre(self):
        if self._method_mgmt_pre=="":
            self._method_mgmt_pre=self.service._getActionMethodMgmt(self.name+"_pre")
        return self._method_mgmt_pre

    @property
    def method_mgmt_post(self):
        if self._method_mgmt_post=="":
            self._method_mgmt_post=self.service._getActionMethodMgmt(self.name+"_post")
        return self._method_mgmt_post

    @property
    def methods(self):
        if not self._methods:
            res = list()
            if self.method_mgmt_pre is not None:
                res.append(self.method_mgmt_pre)
            if self.method_node is not None:
                res.append("node")
            if self.method_mgmt is not None:
                res.append(self.method_mgmt)
            if self.method_mgmt_post is not None:
                res.append(self.method_mgmt_post)
            self._methods=res

        return self._methods


    def log(self,msg):
        print(msg)
        j.atyourservice.alog.log(msg)

    def run(self):
        if len(self.methods)>0:

            self.setState("START")
            print ("RUN:%s"%self)
            for method in self.methods:
                if not self.printonly:
                    if j.atyourservice.debug:
                        # print (method)
                        try:
                            if method == "node":
                                res = self.service._executeOnNode(self.name)
                            else:
                                res = method()
                        except Exception as e:
                            self.setState("ERROR")
                            self.log("Exception:%s"%e)
                            print ("ERROR")
                            raise RuntimeError(e)
                    else:
                        f = io.StringIO()
                        print(1)
                        with redirect_stdout(f):
                            ok=False
                            try:
                                if method == "node":
                                    res = self.service._executeOnNode(self.name)
                                else:
                                    res = method()
                                print ("sdsdsds")
                                raise RuntimeError("1111")
                                ok=True
                            except Exception as e:
                                pass
                        print(2)
                        # self.setState("ERROR")
                        # self.log("STDOUT:")
                        # self.log(f.getvalue())
        else:
            print ("NO METHODS FOR: %s"%self)

        self.setState("OK")

    def __str__(self):
        return ("%-20s -> do: %-30s (%s)"%(self.service,self.name,self.state))

    __repr__=__str__


class Service(object):

    def __init__(self, servicerecipe=None,instance=None, path="", args=None, parent=None, originator=None):
        """
        @param consume is in format $role!$instance,$role2!$instance2
        """
        self.originator = originator

        if path!="" and j.do.exists(path):
            self.role,self.instance=j.sal.fs.getBaseName(path).split("!")
            self._name=None
            self._version=None
            self._domain=None
            self._recipe=None
        else:
            if j.data.types.string.check(servicerecipe):
                raise RuntimeError("no longer supported, pass servicerecipe")
            if servicerecipe==None:
                raise RuntimeError("service recipe cannot be None if path not specified")
            if instance==None:
                raise RuntimeError("instance needs to be specified")
            if path=="":
                raise RuntimeError("path needs to be specified of service")

            self._name = servicerecipe.name.lower()
            self.instance=instance
            self._version = servicerecipe.parent.version
            self._domain = servicerecipe.parent.domain.lower()
            self._recipe = servicerecipe
            self.role = self.name.split(".")[0]

        self.instance = self.instance.lower()

        self._parent = ""
        self._parentChain = None
        if parent is not None:
            self.path = j.sal.fs.joinPaths(parent.path,"%s!%s"%(self.role,self.instance))
            self._parent = parent.key

        self.path = path.rstrip("/")

        self._hrd = None
        self._yaml = None
        self._mongoModel = None

        self._action_methods_mgmt = None
        self._action_methods_node = None

        self._dnsNames = []

        self.args = args or {}
        self._producers = {}
        self.cmd = None
        self._logPath = None

        if self.path == "" or self.path is None:
            raise RuntimeError("cannot be empty")

        self._init = False

        self._state = None

        self._executor = None

        self._recurring = None

        self._actionlog={} #key=actionname with _pre _post ... value = ActionRun

        self.action_current = None
        self._rememberActions = False


    @property
    def key(self):
        return j.atyourservice.getKey(self)

    @property
    def shortkey(self):
        return "%s!%s"%(self.role,self.instance)


    @property
    def name(self):
        if self._name is None:
            self._name=self.hrd.get("service.name")
        return self._name

    @property
    def version(self):
        if self._version is None:
            self._version=self.hrd.get("service.version")
        return self._version

    @property
    def domain(self):
        if self._domain is None:
            self._domain=self.hrd.get("service.domain")
        return self._domain

    @property
    def recipe(self):
        if self._recipe is None:
            self._recipe=j.atyourservice.getRecipe(domain=self.domain, name=self.name, version=self.version)
        return self._recipe

    @property
    def dnsNames(self):
        if self._dnsNames == []:
            self._dnsNames = self.hrd.getList("dns")
        return self._dnsNames

    @property
    def parents(self):
        if self._parentChain ==None:
            chain = []
            parent = self.parent
            while parent is not None:
                chain.append(parent)
                parent = parent.parent
            self._parentChain = chain
        return self._parentChain

    @property
    def parent(self):
        if isinstance(self._parent, str):
            # print ("parent cache miss")
            if self.hrd.exists("parent"):
                role,instance=self.hrd.get("parent").split("!")
                self._parent = j.atyourservice.getService(role,instance)
            else:
                self._parent=None
        return self._parent

    @property
    def hrd(self):
        if self._hrd==None:
            hrdpath = j.sal.fs.joinPaths(self.path, "instance.hrd")
            self._hrd = j.data.hrd.get(hrdpath, prefixWithName=False)
        return self._hrd

    @property
    def yaml(self):
        if self._yaml is None:
            path = j.sal.fs.joinPaths(self.path, "model.yaml")
            if j.sal.fs.exists(path):
                self._yaml = j.data.serializer.yaml.load(path)
        return self._yaml

    @property
    def mongoModel(self):
        if self._mongoModel is None:
            self._mongoModel = self.recipe.model
            if self.yaml:
                for k, v in self.yaml.items():
                    if k in self._mongoModel:
                        self._mongoModel[k] = v
        return self._mongoModel

    @property
    def rememberActions(self):
        return self.hrd.getBool("rememberactions", False)
    

    # @property
    # def hrd_template(self):
    #     if self._hrd_template:
    #         return self._hrd_template
    #     path = j.sal.fs.joinPaths(self.path, "template.hrd")
    #     self._hrd_template = j.data.hrd.get(path, prefixWithName=False)
    #     return self._hrd_template

    @property
    def state(self):
        if self._state==None:
            self._state=None
        return self._state

    @property
    def action_methods_mgmt(self):
        if self._action_methods_mgmt is None:
            if j.sal.fs.exists(path=self.recipe.path_actions_mgmt):
                action_methods_mgmt = self._loadActions(self.recipe.path_actions_mgmt,"mgmt")
            else:
                action_methods_mgmt = j.atyourservice.getActionsBaseClassMgmt()(self)

            if self.rememberActions:
                #we don't want to remember untill hrd is populated
                self._action_methods_mgmt = action_methods_mgmt

        return self._action_methods_mgmt

    @property
    def action_methods_node(self):
        if self._action_methods_node is None:
            if j.sal.fs.exists(path=self.recipe.path_actions_node):
                action_methods_node = self._loadActions(self.recipe.path_actions_node,"node")
            else:
                action_methods_node = j.atyourservice.getActionsBaseClassNode()(self)

            if self.rememberActions:
                #we don't want to remember untill hrd is populated
                self._action_methods_node=action_methods_node

        return self._action_methods_node


    @property
    def actions(self):
        return self._actionlog

    def _setAction(self,name,epoch=0,state="INIT",log=True,printonly=False):
        if name not in self._actionlog:
            self._actionlog[name]=ActionRun(self,name=name,epoch=epoch,state=state,printonly=printonly)
            if log:
                self._actionlog[name].setState(state)
            # print("new action:%s"%self._actionlog[name])
        else:
            actionrun=self._actionlog[name]
            actionrun.printonly=printonly
            if epoch!=0:
                actionrun.epoch=epoch
            if log:
                actionrun.setState(state)
            else:
                actionrun._state=state
            # print("action exists:%s"%self._actionlog[name])


    def getAction(self,name,printonly=False):
        if name not in self._actionlog:
            self._setAction(name,printonly=printonly)
            print("new action:%s (get)"%self._actionlog[name])

        action=self._actionlog[name]
        action.printonly=printonly
        self.action_current=action
        return action


    def runAction(self,name,printonly=False):
        action=self.getAction(name,printonly=printonly)
        action.run()
        return action


    def _getActionMethodMgmt(self,action):
        try:
            method=eval("self.action_methods_mgmt.%s"%action)
        except Exception as e:
            if str(e).find("has no attribute")!=-1:
                return None
            raise RuntimeError(e)
        return method

    def _getActionMethodNode(self,action):
        try:
            method=eval("self.action_methods_node.%s"%action)
        except Exception as e:
            if str(e).find("has no attribute")!=-1:
                return None
            raise RuntimeError(e)
        return method

    def _loadActions(self, path,ttype):
        if j.sal.fs.exists(path+'c'):
            j.sal.fs.remove(path+'c')
        if j.sal.fs.exists(path):
            j.do.createDir(j.do.getDirName(path))
            path2=j.do.joinPaths(self.path,j.do.getBaseName(path))
            j.do.copyFile(path,path2)
            if self._hrd is not None:
                self.hrd.applyOnFile(path2)

            # print ("loadactions:%s:%s:%s"%(self,path,ttype))
            if self.recipe.hrd is not None:
                self.recipe.hrd.applyOnFile(path2)            
            j.application.config.applyOnFile(path2)
        else:
            j.events.opserror_critical(msg="can't find %s." % path, category="ays loadActions")

        modulename = "JumpScale.atyourservice.%s.%s.%s.%s" % (self.domain, self.name, self.instance,ttype)
        mod = loadmodule(modulename, path2)
        #is only there temporary don't want to keep it there
        j.do.delete(path2)
        j.do.delete(j.do.joinPaths(self.path,"__pycache__"))
        return mod.Actions(self)

    @property
    def producers(self):
        if self._producers ==None:
            self._producers={}
            for key, items in self.hrd.getDictFromPrefix("producer").items():
                producerSet = set()
                for item in items:
                    role,instance=item.split("!")
                    service = j.atyourservice.getService(role,instance)
                    producerSet.add(service)

                self._producers[key] = list(producerSet)

            if self.parent is not None:
                self._producers[self.parent.role]=[self.parent]

        return self._producers


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

    def init(self):
        if self._init is False:
            do = False
            if not j.sal.fs.exists(j.sal.fs.joinPaths(self.path, "instance.hrd")):
                do = True
            else:
                changed, changes = j.atyourservice.alog.getChangedAtYourservices("init")
                if self in changed:
                    do = True
            if do:
                print("INIT:%s"%self)
                j.do.createDir(self.path)
                self.runAction("input")
                hrdpath = j.sal.fs.joinPaths(self.path, "instance.hrd")

                # if no schema.hrd exists in servicetemplate, raw yaml will be used as datasource
                # we just create en empty instance.hrd
                if j.sal.fs.exists(self.recipe.parent.path_hrd_schema):
                    self._hrd = self.recipe.schema.hrdGet(hrd=self.hrd, args=self.args)
                else:
                    self._hrd = j.data.hrd.get(hrdpath)

                self.hrd.set("service.name", self.name)
                self.hrd.set("service.version", self.version)
                self.hrd.set("service.domain", self.domain)

                if self.parent is not None:
                    path = j.sal.fs.joinPaths(self.parent.path, "%s!%s" % (self.role, self.instance))
                    if self.path != path:
                        j.sal.fs.moveDir(self.path, path)
                        self.path = path
                        hrdpath = j.sal.fs.joinPaths(self.path, "instance.hrd")
                        self._hrd = j.data.hrd.get(hrdpath, prefixWithName=False)
                    self.consume(self.parent)

                self.runAction("hrd")
                self.hrd.set("rememberActions", True)
                # self.action_methods_mgmt.hrd(self)


        self._init = True

    def consume(self, input):
        """
        @input is comma separate list of ayskeys or a Service object or list of Service object

        ayskeys in format $domain|$name:$instance@role ($version)

        example
        ```
        @input $domain|$name!$instance,$name2!$instance2,$name2,$role4
        ```

        """
        # return
        # if str(input).strip() == "":
        #     return

        emsg = "consume format is: ayskey,ayskey"
        if input is not None and input is not '':
            toConsume = set()
            if j.data.types.string.check(input):
                entities = input.split(",")
                for entry in entities:
                    service = j.atyourservice.getServiceFromKey(entry.strip())
                    toConsume.add(service)

            elif j.data.types.list.check(input):
                for service in input:
                    toConsume.add(service)

            elif isinstance(input, Service):
                toConsume.add(input)
            else:
                j.events.inputerror_critical("Type of input to consume not valid. Only support list, string or Service object", category='AYS.consume', msgpub='Type of input to consume not valid. Only support list, string or Service object')

            for service in toConsume:
                if service.role not in self._producers:
                    self._producers[service.role] = [service]
                else:
                    prodSet = set(self._producers[service.role])
                    prodSet.add(service)
                    self._producers[service.role] = list(prodSet)

            for role, services in self._producers.items():
                producers = set()
                for service in services:
                    producers.add(service.key)
                self.hrd.set("producer.%s" % role, list(producers))

            # walk over the producers
            # for producer in toConsume:
            method=self._getActionMethodMgmt("consume")
            if method:
                    # j.atyourservice.alog.setNewAction(self.role, self.instance, "mgmt","consume")
                self.runAction('consume')
                    # self.action_methods_mgmt.consume(producer)
                    # j.atyourservice.alog.setNewAction(self.role, self.instance, "mgmt","consume","OK")

    def getProducersRecursive(self, producers=set(), callers=set()):
        for role, producers2 in self.producers.items():
            for producer in producers2:
                producers.add(producer)
                producers = producer.getProducersRecursive(producers, callers=callers)
        return producers.symmetric_difference(callers)

    def printProducersRecursive(self,prefix=""):
        for role, producers2 in self.producers.items():
            # print ("%s%s"%(prefix,role))
            for producer in producers2:
                print ("%s- %s"%(prefix,producer))
                producer.printProducersRecursive(prefix+"  ")


    def getProducersWaiting(self, action="install",producersChanged=set()):
        """
        return list of producers which are waiting to be executing the action
        """
        # changed,changes=j.atyourservice.alog.getChangedAtYourservices(action=action)

        # changed2=[]
        # for item in changed:
        #     # print (item.actions)
        #     actionrunobj=item.getAction(action)
        #     if actionrunobj.state!="OK":
        #         changed2.append(item)

        # print ("producerswaiting:%s"%self)
        for producer in self.getProducersRecursive(set(), set()):
            actionrunobj=producer.getAction(action)
            # print (actionrunobj)
            if actionrunobj.state!="OK":
                producersChanged.add(producer)
        return producersChanged


    def getNode(self):
        for parent in self.parents:
            if 'ssh' == parent.role:
                return parent
        return None

    def isOnNode(self,node=None):
        mynode = self.getNode()
        if mynode is None:
            return False
        return mynode.key == node.key


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
        return getProcessDicts(self, args={})

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

    def _uploadToNode(self):
        # ONLY UPLOAD THE SERVICE ITSELF, INIT NEEDS TO BE FIRST STEP, NO IMMEDIATE INSTALL
        if not self.parent or self.parent.role != 'ssh':
        # if "os" not in self.producers:
            return
        hrd_root = "/etc/ays/local/"
        remotePath = j.sal.fs.joinPaths(hrd_root, 'services', j.sal.fs.getBaseName(self.path)).rstrip("/")+"/"
        self.log("uploading %s '%s'->'%s'" % (self.key,self.path,remotePath))
        templatepath = j.sal.fs.joinPaths(hrd_root, 'servicetemplates', j.sal.fs.getBaseName(self.recipe.path).rstrip("/"))
        self.executor.cuisine.dir_ensure(templatepath, recursive=True)
        self.executor.cuisine.dir_ensure(remotePath, recursive=True)
        self.executor.upload(self.recipe.path, templatepath)
        self.executor.upload(self.path, remotePath,recursive=False)

    def _downloadFromNode(self):
        # if 'os' not in self.producers or self.executor is None:
        if not self.parent or self.parent.role != 'ssh':
            return

        hrd_root = "/etc/ays/local/"
        remotePath = j.sal.fs.joinPaths(hrd_root, j.sal.fs.getBaseName(self.path), 'instance.hrd')
        dest = self.path.rstrip("/")+"/"+"instance.hrd"
        self.log("downloading %s '%s'->'%s'" % (self.key, remotePath, self.path))
        self.executor.download(remotePath, self.path)

    def _getExecutor(self):
        # if not self.parent or self.parent.role != 'os':
        # if 'os' in self.producers and len(self.producers["os"]) > 1:
            # raise RuntimeError("found more then 1 executor for %s" % self)

        executor = None
        if self.parent and self.parent.role == 'ssh':
        # if 'os' in self.producers and self.producers.get('os'):
            node = self.parent
            # node = self.producers["os"][0]
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

    def log(self, msg,level=0):
        self.action_current.log(msg)

    def listChildren(self):
        childDirs = j.sal.fs.listDirsInDir(self.path)
        childs = {}
        for path in childDirs:
            child = j.sal.fs.getBaseName(path)
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
    #     @param producerservice is service or servicekey
    #     """
    #     if j.data.types.string.check(producerservice):
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
        if isinstance(service, str):
            return j.atyourservice.getKey(self) == service
        return service.role == self.role and self.instance == service.instance

    def __hash__(self):
      return hash((self.domain, self.name, self.instance, self.role, self.version))

    def __repr__(self):
        # return '%s|%s!%s(%s)' % (self.domain, self.name, self.instance, self.version)
        return self.shortkey

    def __str__(self):
        return self.__repr__()

    # ACTIONS
    # def _executeOnNode(self, actionName, cmd=None, reinstall=False):
    def _executeOnNode(self, actionName):
        if not self.parent or self.parent.role != 'ssh':
        # if 'os' not in self.producers or self.executor is None:
            return False
        self._uploadToNode()

        execCmd = 'source /opt/jumpscale8/env.sh; aysexec do %s %s %s' % (actionName, self.role, self.instance)

        executor = self.executor
        executor.execute(execCmd, die=True, showout=True)

        return True

    # def stop(self):
    #     self.log("stop instance")
    #     self._executeOnNode("stop")
    #     self.recurring.stop()
    #     self.action_methods_mgmt.stop(self)
    #
    #     if not self.action_methods_mgmt.check_down(self):
    #         self.action_methods_mgmt.halt(self)
    #         self._executeOnNode("halt")

    # def start(self):
    #     self.log("start instance")
    #     self._executeOnNode("start")
    #     self.recurring.start()
    #     self.action_methods_mgmt.start(self)
    #
    # def restart(self):
    #     self.stop()
    #     self.start()
    #
    # def prepare(self):
    #     self._executeOnNode("prepare")

    # def install(self, start=True):
    #     """
    #     Install Service.
    #
    #     Keyword arguments:
    #     start     -- whether Service should start after install (default True)
    #     reinstall -- reinstall if already installed (default False)
    #     """
    #
    #     log("INSTALL:%s" % self)
    #
    #     self.action_methods_mgmt.install_pre(self)
    #     if self.state.changed:
    #         self._uploadToNode()
    #     self._executeOnNode('prepare')
    #     self._executeOnNode('install')
    #     self.action_methods_mgmt.install_post(self)
    #
    #     if self.recipe.hrd.getBool("hrd.return", False):
    #         self._downloadFromNode()
    #         # need to reload the downloaded instance.hrd file
    #         self._hrd = j.data.hrd.get(j.sal.fs.joinPaths(self.path, 'instance.hrd'), prefixWithName=False)
    #
    #     # now we can remove changes of statefile & remove old hrd
    #     self.state.installDoneOK()
    #     j.sal.fs.copyFile(
    #         j.sal.fs.joinPaths(self.path, "instance.hrd"),
    #         j.sal.fs.joinPaths(self.path, "instance_old.hrd")
    #     )

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
            self.log("%s cannot be enabled because one or more of its producers is disabled" % self)
            return

        self.state.hrd.set('disabled', False)
        self.log("Enable instance")
        for consumer in self._getConsumers(include_disabled=True):
            consumer.enable()
            consumer.start()

    # def _install(self, reinstall=False):


        # self.configure()

    # def publish(self):
    #     """
    #     check which repo's are used & push the info
    #     this does not use the build repo's
    #     """
    #     if self._executeOnNode("publish"):
    #         return
    #
    #     self.log("publish instance")
    #     self.action_methods_mgmt.publish(self)
    #
    # def package(self):
    #     """
    #     """
    #     if self._executeOnNode("package"):
    #         return
    #
    #     self.action_methods_mgmt.package(self)


    # def update(self):
    #     """
    #     - go over all related repo's & do an update
    #     - copy the files again
    #     - restart the app
    #     """
    #     if self._executeOnNode("update"):
    #         return
    #
    #     self.log("update instance")
    #     for recipeitem in self.hrd.getListFromPrefix("git.export"):
    #         # pull the required repo
    #         j.atyourservice._getRepo(recipeitem['url'], recipeitem=recipeitem)
    #
    #     for recipeitem in self.hrd.getListFromPrefix("git.build"):
    #         # print recipeitem
    #         # pull the required repo
    #         name = recipeitem['url'].replace(
    #             "https://", "").replace("http://", "").replace(".git", "")
    #         dest = "/opt/build/%s/%s" % name
    #         j.do.pullGitRepo(dest=dest, ignorelocalchanges=True)
    #
    #     self.restart()

    # def resetstate(self):
    #     """
    #     remove state of a service.
    #     """
    #     raise RuntimeError("not implemented")
    #     if self._executeOnNode("resetstate"):
    #         return

    #     statePath = j.sal.fs.joinPaths(self.path, 'state.toml')
    #     j.do.delete(statePath)

    # def reset(self):
    #     """
    #     - remove build repo's !!!
    #     - remove state of the app (same as resetstate) in jumpscale (the configuration info)
    #     - remove data of the app
    #     """
    #     if self._executeOnNode("reset"):
    #         return
    #
    #     self.log("reset instance")
    #     # remove build repo's
    #     for recipeitem in self.hrd.getListFromPrefix("git.build"):
    #         name = recipeitem['url'].replace(
    #             "https://", "").replace("http://", "").replace(".git", "")
    #         dest = "/opt/build/%s" % name
    #         j.do.delete(dest)
    #
    #     self.action_methods_mgmt.removedata(self)
    #     j.atyourservice.remove(self)

    # def removedata(self):
    #     """
    #     - remove build repo's !!!
    #     - remove state of the app (same as resetstate) in jumpscale (the configuration info)
    #     - remove data of the app
    #     """
    #     self._executeOnNode("removedata")
    #
    #     self.log("removedata instance")
    #     self.action_methods_mgmt.removedata(self)
    #
    # def execute(self, cmd=None):
    #     """
    #     execute cmd on service
    #     """
    #     if self._executeOnNode("execute", cmd=cmd):
    #         return
    #
    #     if cmd is None:
    #         cmd = self.cmd
    #     self.action_methods_mgmt.execute(self, cmd=cmd)

    # def _uninstall(self):
    #     for recipeitem in self.recipe.hrd.getListFromPrefix("web.export"):
    #         if "dest" not in recipeitem:
    #             raise RuntimeError("could not find dest in hrditem for %s %s" % (recipeitem, self))
    #         dest = recipeitem['dest']
    #         j.sal.fs.removeDirTree(dest)
    #
    #     for recipeitem in self.recipe.hrd.getListFromPrefix("git.export"):
    #         if "platform" in recipeitem:
    #             if not j.core.platformtype.myplatform.checkMatch(recipeitem["platform"]):
    #                 continue
    #
    #         if "link" in recipeitem and str(recipeitem["link"]).lower() == 'true':
    #             # means we need to only list files & one by one link them
    #             link = True
    #         else:
    #             link = False
    #
    #         repository_type, repository_account, repository_name = recipeitem['url'].strip('http://').strip('https://').split('/', 3) #'http://git.aydo.com/binary/mongodb',
    #         repository_type = repository_type.split('.')[0]
    #         srcdir = '%(codedir)s/%(type)s/%(account)s/%(repo_name)s' % {
    #             'codedir': j.dirs.codeDir,
    #             'type': repository_type.lower(),
    #             'account': repository_account.lower(),
    #             'repo_name': repository_name,
    #         }
    #
    #         src = recipeitem['source']
    #         src = j.sal.fs.joinPaths(srcdir, src)
    #
    #         if "dest" not in recipeitem:
    #             raise RuntimeError(
    #                 "could not find dest in hrditem for %s %s" % (recipeitem, self))
    #         dest = recipeitem['dest']
    #
    #         if src[-1] == "*":
    #             src = src.replace("*", "")
    #             if "nodirs" in recipeitem and str(recipeitem["nodirs"]).lower() == 'true':
    #                 # means we need to only list files & one by one link them
    #                 nodirs = True
    #             else:
    #                 nodirs = False
    #
    #             items = j.do.listFilesInDir(
    #                 path=src, recursive=False, followSymlinks=False, listSymlinks=False)
    #             if nodirs is False:
    #                 items += j.do.listDirsInDir(
    #                     path=src, recursive=False, dirNameOnly=False, findDirectorySymlinks=False)
    #
    #             items = [(item, "%s/%s" % (dest, j.do.getBaseName(item)), link)
    #                      for item in items]
    #         else:
    #             items = [(src, dest, link)]
    #
    #         for src, dest, link in items:
    #             if dest.strip() == "":
    #                 raise RuntimeError("a dest in coderecipe cannot be empty for %s" % self)
    #             if dest[0] != "/":
    #                 dest = "/%s" % dest
    #             else:
    #                 if link:
    #                     if j.sal.fs.exists(dest):
    #                         j.sal.fs.unlink(dest)
    #                 else:
    #                     self.log(("deleting: %s" % dest))
    #                     j.sal.fs.removeDirTree(dest)

    # def uninstall(self):
    #     self._executeOnNode("uninstall")
    #
    #
    #     self.log("uninstall instance")
    #     self.disable()
    #     self._uninstall()
    #     self.action_methods_mgmt.uninstall(self)
    #     j.sal.fs.removeDirTree(self.path)
    #
    # def monitor(self):
    #     """
    #     Schedule the monitor local and monitor remote methods
    #     """
    #     if self._executeOnNode("monitor"):
    #         res = self.action_methods_mgmt.check_up_local(self)
    #         res = res and self.action_methods_mgmt.schedule_monitor_local(self)
    #         res = res and self.action_methods_mgmt.schedule_monitor_remote(self)
    #         return res
    #
    #     return True

    # def iimport(self, url):
    #     if self._executeOnNode("import"):
    #         return
    #
    #     self.log("import instance data")
    #     self.action_methods_mgmt.data_import(url, self)
    #
    # def export(self, url):
    #     if self._executeOnNode("export"):
    #         return
    #
    #     self.log("export instance data")
    #     self.actions.data_export(url, self)
    #
    # def configure(self, restart=True):
    #
    #     self.log("configure instance mgmt")
    #     res = self.action_methods_mgmt.configure(self)
    #     if res is False:
    #         j.events.opserror_critical(msg="Could not configure %s (mgmt)" % self, category="ays.service.configure")
    #
    #     self.log("configure instance on node")
    #     self._executeOnNode("configure")
