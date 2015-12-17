from JumpScale import j
from OSISCMDS import OSISCMDS
from OSISClientForCat import OSISClientForCat
from OSISBaseObject import OSISBaseObject
from OSISBaseObjectComplexType import OSISBaseObjectComplexType
import JumpScale.baselib.codegentools
import JumpScale.baselib.codetools

import inspect
import imp
import sys
import ujson
import lz4


class FileLikeStreamObject(object):
    def __init__(self):
        self.out=""

    def write(self, buf,**args):
        for line in buf.rstrip().splitlines():
            #print "###%s"%line
            self.out+="%s\n"%line

class ClassEmpty():
    pass

class NameSpaceClient(object):
    def __init__(self, client, namespace):
        self._client = client
        self._namespace = namespace
        for category in client.listNamespaceCategories(namespace):
            cclient = j.clients.osis.getCategory(self._client, self._namespace, category)
            setattr(self, category, cclient)

    def __getattr__(self, category):
        categories = self._client.listNamespaceCategories(self._namespace)
        if category not in categories:
            raise AttributeError("Category %s does not exists in namespace %s" % (category, self._namespace))

        cclient = j.clients.osis.getCategory(self._client, self._namespace, category)
        setattr(self, category, cclient)
        return cclient

class OSISClientFactory(object):
    def __init__(self):
        self.__jslocation__ = "j.clients.osis"
        self._sysstdout = None
        self.osisConnections = {}
        self.osisConnectionsCat={}

    def get(self, ipaddr=None, port=5544,user=None,passwd=None,ssl=False,gevent=False):
        if ipaddr==None or user==None or passwd==None:
            osisInstances=j.atyourservice.findServices(name="osis_client",domain="jumpscale")
            # inames=osisays.listInstances()
            if len(osisInstances)>0:
                osisService = osisInstances[0]
                # osisays=osisays.load(instance=inames[0])
                hrd=osisService.hrd
                if ipaddr==None:
                    ipaddr=hrd.get("param.osis.client.addr")
                if user==None:
                    user=hrd.get("param.osis.client.login")
                if passwd==None:
                    passwd=hrd.get("param.osis.client.passwd")
                port=int(hrd.get("param.osis.client.port"))

        if passwd=="EMPTY":
            passwd=""

        if ipaddr!=None:
            if not isinstance(ipaddr, list):
                ips = [ipaddr]
            else:
                ips = ipaddr
        elif j.application.config.exists('osis.ip'):
            ips = j.application.config.getList('osis.ip')
        else:
            ips = [ j.application.config.get('grid.master.ip') ]
        connections = [ (ip, port) for ip in ips ]
        key = "%s_%s_%s" % (connections, user, passwd)
        if key in self.osisConnections:
            return self.osisConnections[key]

        if user==None or user=="node":
            user="node"
            passwd=j.application.config.get("grid.node.machineguid")
        elif user=="root" and not passwd:
            if j.application.config.exists("osis.superadmin.passwd"):
                passwd=j.application.config.get("osis.superadmin.passwd")
            else:
                raise RuntimeError("Osis superadmin passwd has not been defined on this node, please put in #hrd (osis.superadmin.passwd) or use argument 'passwd'.")

        with j.logger.nostdout():
            client= j.servers.geventws.getClient(connections[0][0], connections[0][1], user=user, passwd=passwd,category="osis")
        self.osisConnections[key] = client
        return client

    def getByInstance(self, instance=None, ssl=False, gevent=False,die=True):
        if instance is None:
            if hasattr(j.application, 'instanceconfig'):
                services = j.application.instanceconfig.getListFromPrefix('producer.osis_client')[0]
                if len(services) < 0:
                    instance = 'main'
                else:
                    _, _, _, instance, _ = j.atyourservice.parseKey(services[0])
            else:
                instance = 'main'
        hrdinstance = j.atyourservice.getService(role="osis_client",instance=instance).hrd
        if hrdinstance:
            ipaddr = hrdinstance.getList("param.osis.client.addr")
            port = int(hrdinstance.get("param.osis.client.port"))
            user = hrdinstance.get("param.osis.client.login")
            passwd = hrdinstance.get("param.osis.client.passwd")
            return self.get(ipaddr=ipaddr, port=port, user=user, passwd=passwd, ssl=ssl, gevent=gevent)
        if die:
            j.events.inputerror_critical("Could not find osis_client with instance:%s, could not load osis,"%instance)

    def getNamespace(self, namespace, client=None):
        if client==None:
            client = self.getByInstance(None)  # None force to use instance from producers
        return NameSpaceClient(client, namespace)

    def getCategory(self, client, namespace, category):
        """
        how to use
        @param client: osiclient
        @param namespace: OSIS namespace
        @param category: OSIS category

        """
        if client==None:
            raise RuntimeError("Client cannot be None: getCategory %s/%s"%(namespace, category))
        return OSISClientForCat(client, namespace, category)



class OSISFactory:

    """
    """

    def __init__(self):
        self.__jslocation__ = "j.core.osis"
        self.nodeguids={}
        self.osisModels={}
        self.namespacesInited={}
        

    def encrypt(self,obj):
        if isinstance(obj, str):
            obj = str(obj)
        if not j.core.types.string.check(obj):
            if j.core.types.dict.check(obj):
                val=obj
            else:
                val=obj.__dict__
            val=ujson.dumps(val)
        else:
            val = obj
        val=lz4.dumps(val)
        val=j.data.serializer.serializers.blowfish.dumps(val,self.key)
        return val

    def decrypt(self,val,json=False):
        if not j.core.types.string.check(val):
            raise RuntimeError("needs to be string")
        val=j.data.serializer.serializers.blowfish.loads(val,self.key)
        val=lz4.loads(val)
        if json:
            val=ujson.loads(val)
        return val

    def getLocal(self, path="", overwriteHRD=False, overwriteImplementation=False, namespacename=None):
        """
        create local instance starting from path
        """
        osis=OSISCMDS()
        osis.init()
        return osis

    def startDaemon(self, path="", overwriteHRD=False, overwriteImplementation=False, key="",port=5544,superadminpasswd=None,dbconnections={},hrd=None):
        """
        start deamon
        """
        if hrd!=None:
            self.hrd=hrd
        self.key=key
        self.superadminpasswd=superadminpasswd
        self.dbconnections=dbconnections

        if self.superadminpasswd=="":
             j.events.inputerror_critical("cannot start osis, superadminpasswd needs to be specified")

        daemon = j.servers.geventws.getServer(port=port)
        OSISCMDS.dbconnections = dbconnections
        daemon.addCMDsInterface(OSISCMDS, category="osis")  # pass as class not as object !!!
        daemon.daemon.cmdsInterfaces["osis"].init(path=path)#,esip=elasticsearchip,esport=elasticsearchport,db=db)
        self.cmds=daemon.daemon.cmdsInterfaces["osis"]
        # daemon.schedule("checkchangelog", self.cmds.checkChangeLog)
        daemon.start()


    def getOsisBaseObjectClass(self):
        return OSISBaseObject

    def getOSISBaseObjectComplexType(self):
        return OSISBaseObjectComplexType

    def getOsisImplementationParentClass(self, namespacename):
        """
        return parent class for osis implementation (is the implementation from which each namespace & category inherits)
        """
        implpath = j.sal.fs.joinPaths("logic", namespacename, "OSIS_parent.py")
        classs = self._loadModuleClass(implpath)
        return classs

    def _generateOsisModelClassFromSpec(self,namespace,specpath,modelName="",classpath=""):
        """
        generate class files for spec (can be more than 1)
        generated in classpath/modelName/OsisGeneratedRootObject.py
        and also classpath/modelName/model.py
        @return classpath
        """
        import JumpScale.baselib.specparser                
        j.core.specparser.parseSpecs(specpath, appname="osismodel", actorname=namespace)

        modelNames = j.core.specparser.getModelNames("osismodel", namespace)

        if classpath=="":
            classpath=j.sal.fs.joinPaths(j.dirs.varDir,"code","osismodel",namespace)

        extpath=j.sal.fs.getDirName(inspect.getfile(j.clients.osis.get))
        templpath=j.sal.fs.joinPaths(extpath,"_templates","osiscomplextypes")
        j.sal.fs.copyDirTree(templpath, classpath, keepsymlinks=False, eraseDestination=False, \
            skipProtectedDirs=False, overwriteFiles=False, applyHrdOnDestPaths=None)        
                
        if len(modelNames) > 0:

            for modelName in modelNames:
                modelspec = j.core.specparser.getModelSpec("osismodel", namespace, modelName)
                modeltags = j.data.tags.getObject(modelspec.tags)

                # # will generate the tasklets
                # modelHasTasklets = modeltags.labelExists("tasklets")
                # if modelHasTasklets:
                #     j.core.codegenerator.generate(modelspec, "osis", codepath=actorpath, returnClass=False, args=args)

                # if spec.hasTasklets:
                #     self.loadOsisTasklets(actorobject, actorpath, modelName=modelspec.name)

                code = j.core.codegenerator.getCodeJSModel("osismodel", namespace, modelName)
                if modelspec.tags == None:
                    modelspec.tags = ""
                index = j.data.tags.getObject(modelspec.tags).labelExists("index")
                tags = j.data.tags.getObject(modelspec.tags)

                classnameGenerated="JSModel_%s_%s_%s"%("osismodel", namespace, modelName)
                classnameNew="%s_%s"%(namespace,modelName)
                classnameNew2="%s_%s_osismodelbase"%(namespace,modelName)
                code=code.replace(classnameGenerated,classnameNew2)

                classpathForModel=j.sal.fs.joinPaths(classpath,modelName)
                j.sal.fs.createDir(classpathForModel)
                classpath3=j.sal.fs.joinPaths(classpathForModel,"%s_osismodelbase.py"%classnameNew)
                j.sal.fs.writeFile(filename=classpath3,contents=code)

                mpath=j.sal.fs.joinPaths(classpathForModel,"model.py")
                if not j.sal.fs.exists(path=mpath):
                    j.sal.fs.copyFile(j.sal.fs.joinPaths(classpath,"model_template.py"),mpath)
                    content=j.sal.fs.fileGetContents(mpath)
                    content=content.replace("$modelbase","%s"%classnameNew)
                    j.sal.fs.writeFile(filename=mpath,contents=content)

        return classpath

    def generateOsisModelDefaults(self,namespace,specpath=""):
        import JumpScale.baselib.codegentools

        if specpath=="":
            specpath=j.sal.fs.joinPaths("logic", namespace, "model.spec")

        basepathspec=j.sal.fs.getDirName(specpath)


        if j.sal.fs.exists(path=specpath):
            self._generateOsisModelClassFromSpec(namespace,specpath=basepathspec,classpath=basepathspec)

    def getModelTemplate(self):
        extpath=j.sal.fs.getDirName(inspect.getfile(j.clients.osis.get))
        return j.sal.fs.joinPaths(extpath,"_templates","model_template.py")


    def getOsisModelClass(self,namespace,category,specpath=""):
        """
        returns class generated from spec file or from model.py file
        """
        key="%s_%s"%(namespace,category)

        if key not in self.osisModels:
            # #need to check if there is a specfile or we go from model.py  
            if specpath=="":
                specpath=j.sal.fs.joinPaths("logic", namespace, "model.spec")            

            basepathspec=j.sal.fs.getDirName(specpath)            
            basepath=j.sal.fs.joinPaths(basepathspec,category)            
            modelpath=j.sal.fs.joinPaths(basepath,"model.py")

            if j.sal.fs.exists(path=modelpath):
                if  '__pycache__' in modelpath:
                    return
                klass= j.sal.fs.fileGetContents(modelpath)
                name=""
                for line in klass.split("\n"):
                    if line.find("(OsisBaseObject")!=-1 and line.find("class ")!=-1:
                        name=line.split("(")[0].lstrip("class").strip()
                if name=="":
                    raise RuntimeError("could not find: class $modelName(OsisBaseObject) in model class file, should always be there")

                sys.path.append(basepath)
                module = imp.load_source(key,modelpath)
                self.osisModels[key]=module.__dict__[name]
            else:
                raise RuntimeError("Could not find model.py in %s"%basepath)

        return self.osisModels[key]

    def _loadModuleClass(self, path):
        '''Load the Python module from disk using a random name'''
        modname = "osis_%s"%path.replace("/","_").replace("logic_","")[:-3]
        
        # while modname in sys.modules:
        #     modname = generate_module_name()

        module = imp.load_source(modname, path)
        # find main classname of module
        # classes=[item for item in module.__dict__.keys() if (item != "q" and item[0] != "_")]
        # if len(classes) != 1:
        #     j.errorconditionhandler.raiseBug(message="there must be only 1 class implemented in %s"%path,category="osis.init")
        # classname=classes[0]
        # return module.__dict__[classname]
        try:
            return module.mainclass
        except Exception as e:
            raise RuntimeError("Could not load module on %s, could not find 'mainclass', check code on path. Error:%s"% (path,e))
            
