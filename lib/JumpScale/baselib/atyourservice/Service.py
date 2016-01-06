from JumpScale import j
# import JumpScale.baselib.actions

# import pytoml

import imp
import sys
from functools import wraps
from Recurring import Recurring

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


        self._parent = None
        self._parentChain = None

        self.path = path.rstrip("/")

        self._hrd = None

        if parent!=None:
            self.path=j.sal.fs.joinPaths(parent.path,"%s!%s"%(self.role,self.instance))
            self.hrd.set("parent",parent)

        self._actions_mgmt = None
        self._actions_node = None

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

        if not j.do.exists(self.path):
            self.init()

    @property
    def key(self):
        return j.atyourservice.getKey(self)

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


    # @property
    # def template(self):
    #     if self._recipe is None:
    #         self._recipe=j.atyourservice.getTemplate(domain=self.domain, name=self.name, version=self.version)
    #     return self._recipe

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
        if self._parentChain ==[]:
            chain = []
            parent = self.parent
            while parent is not None:
                chain.append(parent)
                parent = parent.parent
            self._parentChain = chain
        return self._parentChain

    @property
    def parent(self):
        if self._parent ==None:
            self._parent = j.atyourservice.getServiceFromKey(self.hrd.get("parent"))
        return self._parent

    @property
    def hrd(self):
        if self._hrd==None:
            hrdpath = j.sal.fs.joinPaths(self.path, "instance.hrd")
            self._hrd = j.data.hrd.get(hrdpath, prefixWithName=False)
        return self._hrd

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
    def actions_mgmt(self):
        if self._actions_mgmt is None:
            if j.sal.fs.exists(path=self.recipe.path_actions_mgmt):
                self._actions_mgmt = self._loadActions(self.recipe.path_actions_mgmt,"mgmt")                
            else:
                self._actions_mgmt = j.atyourservice.getActionsBaseClassMgmt()()

        return self._actions_mgmt

    @property
    def actions_node(self):
        if self._actions_node is None:
            if j.sal.fs.exists(path=self.recipe.path_actions_node):
                self._actions_mgmt = self._loadActions(self.recipe.path_actions_node,"node")
            else:
                self._actions_node = j.atyourservice.getActionsBaseClassNode()()

        return self._actions_node

    def _loadActions(self, path,ttype):
        if j.sal.fs.exists(path+'c'):
            j.sal.fs.remove(path+'c')
        if j.sal.fs.exists(path):
            j.do.createDir(j.do.getDirName(path))
            path2=j.do.joinPaths(self.path,j.do.getBaseName(path))
            j.do.copyFile(path,path2)
            if self._hrd is not None:
                self.hrd.applyOnFile(path2)
            j.application.config.applyOnFile(path2)
        else:
            j.events.opserror_critical(msg="can't find %s." % path, category="ays loadActions")

        modulename = "JumpScale.atyourservice.%s.%s.%s.%s" % (self.domain, self.name, self.instance,ttype)
        mod = loadmodule(modulename, path2)
        #is only there temporary don't want to keep it there
        j.do.delete(path2)
        j.do.delete(j.do.joinPaths(self.path,"__pycache__"))
        return mod.Actions()        

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
            self._logPath = j.sal.fs.joinPaths(self.path, "log.txt")
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

    def init(self):
        if self._init is False:
            print ("init:%s"%self)
            j.do.createDir(self.path)
            self.actions_mgmt.input(self)  #we now init the full service object and can be fully manipulated there even changing the hrd
            hrdpath = j.sal.fs.joinPaths(self.path, "instance.hrd")
            self._hrd=self.recipe.schema.hrdGet(hrd=self.hrd,args=self.args)
            self.hrd.set("service.name",self.name)
            self.hrd.set("service.version",self.version)
            self.hrd.set("service.domain",self.domain)
            self.actions_mgmt.hrd(self)

            if self._parent!=None:
                path=j.sal.fs.joinPaths(self.parent.path,"%s!%s"%(self.role,self.instance))
                if self.path!=path:
                    j.sal.fs.moveDir(self.path,path)
                    self.path=path

            
        self._init = True

    # def _apply(self):
        # log("apply")
        # j.do.createDir(self.path)

        # make sure they are loaded (properties), otherwise paths will be wrong
        # self.recipe.hrd #still required?

        # source = self.recipe.path_hrd_template
        # j.do.copyFile(source, "%s/template.hrd" % self.path)

        # path_templatehrd = "%s/template.hrd" % self.path
        # tmpl_hrd = j.data.hrd.get(path_templatehrd, prefixWithName=False)

        # tmpl_hrd.set('domain', self.domain)
        # tmpl_hrd.set('name', self.name)
        # tmpl_hrd.set('version', self.version)
        # tmpl_hrd.set('instance', self.instance)
        # tmpl_hrd.process()  # force replacement of $() inside the file itself

        # path_instancehrd_new="%s/instance.hrd" % self.path
        # path_instancehrd_old="%s/instance_old.hrd" % self.path

        # # print path_instancehrd_old
        # if not j.sal.fs.exists(path=path_instancehrd_new):
        #     path_instancehrd = "%s/instance_.hrd" % self.path
        #     source = self.recipe.path_hrd_instance
        #     j.do.copyFile(source, path_instancehrd)

        #     hrd = j.data.hrd.get(path_instancehrd, prefixWithName=False)
        #     args0 = {}
        #     for key, item in self.recipe.hrd_instance.items.items():
        #         if item.data.startswith("@ASK"):
        #             args0[key] = item.data
        #         else:
        #             args0[key] = item.get()
        #     args0.update(self.args)

        #     # here the args can be manipulated
        #     if self.actions_mgmt != None:
        #         self.actions_mgmt.input(self, args0)
        #     self._actions_mgmt = None  # force to reload later with new value of hrd

        #     hrd.setArgs(args0)

        #     for key,item in hrd.items.items():
        #         if j.data.types.string.check(item.data) and item.data.find("@ASK") != -1:
        #             item.get() #SHOULD DO THE ASK

        #     # producers0={}
        #     # for key, services in self._producers.items():#hrdnew.getDictFromPrefix("producer").iteritems():
        #     # #     producers0[key]=[j.atyourservice.getServiceFromKey(item.strip()) for item in item.split(",")]

        #     # # for role,services in producers0.iteritems():
        #     #     producers=[]
        #     #     for service in services:
        #     #         key0=j.atyourservice.getKey(service)
        #     #         if key0 not in producers:
        #     #             producers.append(key0)
        #     #     hrd.set("producer.%s"%key,producers)

        #     if self.parent or self._parentkey != '':
        #         hrd.set('parent', self._parentkey)

        #     self._hrd = hrd

        #     j.application.config.applyOnFile(path_instancehrd)
        #     # hrd.applyOnFile(path_templatehrd)
        #     # hrd.save()

        #     j.sal.fs.moveFile(path_instancehrd,path_instancehrd_new)
        #     path_instancehrd=path_instancehrd_new

        #     hrd.path=path_instancehrd

        #     # check if 1 of parents is of type node
        #     # if self.parent and self.parent.role == "os":
        #         # self.consume(self.parent)

        # else:
        #     hrd=j.data.hrd.get(path_instancehrd_new)
        #     path_instancehrd=path_instancehrd_new

        # hrd.applyOnFile(path_templatehrd)
        # j.application.config.applyOnFile(path_templatehrd)
        # tmpl_hrd = j.data.hrd.get(path_templatehrd, prefixWithName=False)

        # actionPy = j.sal.fs.joinPaths(self.path, "actions_mgmt.py")
        # if j.sal.fs.exists(path=actionPy):
        #     hrd.applyOnFile(actionPy) #@todo somewhere hrd gets saved when doing apply (WHY???)
        #     tmpl_hrd.applyOnFile(actionPy)
        #     j.application.config.applyOnFile(actionPy)
        # actionPy = j.sal.fs.joinPaths(self.path, "actions_node.py")
        # if j.sal.fs.exists(path=actionPy):
        #     hrd.applyOnFile(actionPy) #@todo somewhere hrd gets saved when doing apply (WHY???)
        #     tmpl_hrd.applyOnFile(actionPy)
        #     j.application.config.applyOnFile(actionPy)

        # self._state=ServiceState(self)

        # # not sure this code is this code is still relevent here, cause the _apply()
        # # method is now only called once at service init.
        # change=self.state.changed

        # if change:
        #     #found changes in hrd or one of the actionfiles
        #     oldhrd_exists=j.sal.fs.exists(path=path_instancehrd_old)
        #     if not oldhrd_exists:
        #         j.do.writeFile(path_instancehrd_old,"")

        #     hrdold=j.data.hrd.get(path_instancehrd_old)

        #     self.state.commitHRDChange(hrdold,hrd)

        #     # res=self.actions_mgmt.configure(self)
        #     # if res==False:
        #         # j.events.opserror_critical(msg="Could not configure %s (mgmt)" % self, category="ays.service.configure")

        # self._hrd=hrd

        # if self.state.changed:
        #     self.state.saveState()        

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
            elif j.data.types.list.check(input):
                for serv in input:
                    self.consume(serv)
            else:
                entities = input.split(",")
                for entry in entities:
                    print("get service for consumption:%s" % entry.strip())
                    service = j.atyourservice.getServiceFromKey(entry.strip())
                    if service.role not in self._producers:
                        self._producers[service.role] =  [service]
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

            # if self._hrd is not None:
            self.hrd.set("producer.%s" % key, producers)

        #walk over the producers
        for producer in services:
            self.actions_mgmt.consume(self, producer)

        print("consumption done")

    def check(self):
        """
        check if template file changed with local
        """
        self._apply()
        if self.state.changed:
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
                if producer.state.changed:
                    producersChanged.add(producer)
        return producersChanged

    def getNode(self):
        for parent in self.parents:
            if 'os' == parent.role:
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
    #     checksumpath = j.sal.fs.joinPaths(self.path, "installed.version")
    #     #@todo how can this ever be different, doesn't make sense to me? (despiegk)
    #     installedchecksum = j.sal.fs.fileGetContents(checksumpath).strip()
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

    #         current = j.sal.process.execute(
    #             'cd %s; git rev-parse HEAD --branch %s' % (dest, branch))
    #         current = current[1].split('--branch')[1].strip()
    #         remote = j.sal.process.execute(
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
        return getProcessDicts(self.recipe.hrd, args={})

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


    def _findMethod(self,templatepath,methodname):
        methodname=methodname.strip()
        if not j.sal.fs.exists(path=templatepath):
            raise RuntimeError("Cannot find template:%s, as I need it to find inheritance for %s"%(templatepath,self))
        C2=j.do.readFile(templatepath)
        out=""
        state="start"
        for line in C2.split("\n"):
            line=line.replace("\t","    ")

            if state=="found" and line.startswith("    def"):
                break

            if line.startswith("    def %s"%methodname):
                state="found"

            if state=="found":
                out+="%s\n"%line

        if out.strip()=="":
            raise RuntimeError("Cannot find template:%s method %s, as I need it to find inheritance for %s"%(templpath2,methodname,self))


        return out.rstrip()


    def _processInheritance(self,templatepath,outpath):
        C=j.do.readFile(templatepath)
        found=False
        if C.find("@INHERIT")!=-1:
            out=""
            for line in C.split("\n"):
                if line.find("@INHERIT")!=-1:
                    nothing,templatename,methodnames=line.split(":",2)
                    templ=j.atyourservice.getTemplate(name=templatename)
                    templpath2=templ.path+"/"+j.sal.fs.getBaseName(templatepath)
                    for methodname in methodnames.split(","):
                        C3=self._findMethod(templpath2,methodname)
                        out+="\n\n%s\n\n"%C3
                        found=True
                    continue

                out+="%s\n"%line
            j.do.writeFile(outpath,out)

        return found



    def _uploadToNode(self):
        # ONLY UPLOAD THE SERVICE ITSELF, INIT NEEDS TO BE FIRST STEP, NO IMMEDIATE INSTALL
        if not self.parent or self.parent.role != 'os':
        # if "os" not in self.producers:
            return
        hrd_root = "/etc/ays/local/"
        remotePath = j.sal.fs.joinPaths(hrd_root, j.sal.fs.getBaseName(self.path)).rstrip("/")+"/"
        print("uploading %s '%s'->'%s'" % (self.key,self.path,remotePath))
        self.executor.upload(self.path, remotePath,recursive=False)


    def _downloadFromNode(self):
        # if 'os' not in self.producers or self.executor is None:
        if not self.parent or self.parent.role != 'os':
            return

        hrd_root = "/etc/ays/local/"
        remotePath = j.sal.fs.joinPaths(hrd_root, j.sal.fs.getBaseName(self.path), 'instance.hrd')
        dest = self.path.rstrip("/")+"/"+"instance.hrd"
        print("downloading %s '%s'->'%s'" % (self.key, remotePath, self.path))
        self.executor.download(remotePath, self.path)

    def _getExecutor(self):
        # if not self.parent or self.parent.role != 'os':
        # if 'os' in self.producers and len(self.producers["os"]) > 1:
            # raise RuntimeError("found more then 1 executor for %s" % self)

        executor = None
        if self.parent and self.parent.role == 'os':
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

    def log(self, msg):
        logpath = j.sal.fs.joinPaths(self.path, "log.txt")
        if not j.sal.fs.exists(self.path):
            j.sal.fs.createDir(self.path)
        msg = "%s : %s\n" % (
            j.data.time.formatTime(j.data.time.getTimeEpoch()), msg)
        j.sal.fs.writeFile(logpath, msg, append=True)

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
    #     @param producerservice is serviceObj or servicekey
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
        return service.role == self.role and self.instance == service.instance

    def __hash__(self):
      return hash((self.domain, self.name, self.instance, self.role, self.version))

    def __repr__(self):
        return '%s|%s!%s(%s)' % (self.domain, self.name, self.instance, self.version)

    def __str__(self):
        return self.__repr__()

    # ACTIONS
    def _executeOnNode(self, actionName, cmd=None, reinstall=False):
        if not self.parent or self.parent.role != 'os':
        # if 'os' not in self.producers or self.executor is None:
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
        # for key, producers in self.producers.items():
        #     for producer in producers:
                # self.actions_mgmt.consume(self, producer)
        # self._apply()

        # if self.state.changed:
        #     self._uploadToNode()
        #
        # self._executeOnNode('install')
        #
        # self.stop()
        # self.prepare()
        #
        # # self._install()
        # self.configure()
        #
        # # now we can remove changes of statefile & remove old hrd
        # self.state.installDoneOK()
        # j.sal.fs.copyFile(
        #     j.sal.fs.joinPaths(self.path, "instance.hrd"),
        #     j.sal.fs.joinPaths(self.path, "instance_old.hrd")
        # )
        #
        # if start:
        #     self.start()
        #

        self.actions_mgmt.install_pre(self)
        if self.state.changed:
            self._uploadToNode()
        self._executeOnNode('prepare')
        self._executeOnNode('install')
        self.actions_mgmt.install_post(self)

        if self.recipe.hrd.getBool("hrd.return", False):
            self._downloadFromNode()
            # need to reload the downloaded instance.hrd file
            self._hrd = j.data.hrd.get(j.sal.fs.joinPaths(self.path, 'instance.hrd'), prefixWithName=False)

        # now we can remove changes of statefile & remove old hrd
        self.state.installDoneOK()
        j.sal.fs.copyFile(
            j.sal.fs.joinPaths(self.path, "instance.hrd"),
            j.sal.fs.joinPaths(self.path, "instance_old.hrd")
        )
        # if res is False:
        #     j.events.opserror_critical(msg="Could not install (mgmt) %s" % self, category="ays.service.install")
        #
        # restart = False
        # if res == "r":
        #     restart = True
        # if restart:
        #     self.restart()




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

        statePath = j.sal.fs.joinPaths(self.path, 'state.toml')
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
        for recipeitem in self.recipe.hrd.getListFromPrefix("web.export"):
            if "dest" not in recipeitem:
                raise RuntimeError("could not find dest in hrditem for %s %s" % (recipeitem, self))
            dest = recipeitem['dest']
            j.sal.fs.removeDirTree(dest)

        for recipeitem in self.recipe.hrd.getListFromPrefix("git.export"):
            if "platform" in recipeitem:
                if not j.core.platformtype.checkMatch(recipeitem["platform"]):
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
            src = j.sal.fs.joinPaths(srcdir, src)

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
                        if j.sal.fs.exists(dest):
                            j.sal.fs.unlink(dest)
                    else:
                        print(("deleting: %s" % dest))
                        j.sal.fs.removeDirTree(dest)

    def uninstall(self):
        self._executeOnNode("uninstall")


        self.log("uninstall instance")
        self.disable()
        self._uninstall()
        self.actions_mgmt.uninstall(self)
        j.sal.fs.removeDirTree(self.path)

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

        self.log("configure instance mgmt")
        res = self.actions_mgmt.configure(self)
        if res is False:
            j.events.opserror_critical(msg="Could not configure %s (mgmt)" % self, category="ays.service.configure")

        self.log("configure instance on node")
        self._executeOnNode("configure")
