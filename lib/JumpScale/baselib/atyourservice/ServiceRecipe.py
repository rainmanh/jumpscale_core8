

from JumpScale import j

# import JumpScale.baselib.actions

from ServiceTemplate import ServiceTemplate
from Service import Service

class ActionMethod():

    def __init__(self,recipe,name,content):
        self.name=name
        self.recipe=recipe
        self._check(content)
        self.hrdArgKeys=[] #names of arguments as used in hrd which are used in this action method
        if content=="":
            self.hash=""
        else:
            self.hash=j.data.hash.md5_string(content)

    def _check(self,content):
        #for now we don't do a check, later want to make sure we don't call other services, now we just put impact on all hrd schema arguments
        self.recipe.schema
        #for now we take all arguments, later we need to be more specific
        self.hrdArgKeys=[item for item in self.recipe.schema.items.keys()]

    def __repr__(self):
        return "%s:%s"%(self.name,self.hash)

    __str__=__repr__



class ServiceRecipe(ServiceTemplate):

    def __init__(self, path="",template=None,aysrepopath=""):

        aysrepopath = j.atyourservice.basepath
        if not aysrepopath:
            raise j.exceptions.RuntimeError("A service instance can only be used when used from a ays repo")

        if path != "":
            if not j.sal.fs.exists(path):
                raise j.exceptions.RuntimeError("Could not find path for recipe")
            self.path = path
            name = self.state.hrd.get("template.name")
            domain = self.state.hrd.get("template.domain")
            version = self.state.hrd.get("template.version")
            self.template = j.atyourservice.getTemplate(domain=domain, name=name, version=version)
            self.name = self.template.name
        else:
            self.path = j.sal.fs.joinPaths(aysrepopath,"recipes", template.name)
            self.name = template.name
            self.template = template

        # copy the files
        if not j.sal.fs.exists(path=self.path):
            firstime = True
            j.sal.fs.createDir(self.path)
        else:
            firstime = False

        self.actionmethods={}

        self._init()

        if j.sal.fs.exists(self.template.path_hrd_template):
            j.sal.fs.copyFile(self.template.path_hrd_template, self.path_hrd_template)
        if j.sal.fs.exists(self.template.path_hrd_schema):
            j.sal.fs.copyFile(self.template.path_hrd_schema, self.path_hrd_schema)
        if j.sal.fs.exists(self.template.path_actions_node):
            j.sal.fs.copyFile(self.template.path_actions_node, self.path_actions_node)
        if j.sal.fs.exists(self.template.path_mongo_model):
            j.sal.fs.copyFile(self.template.path_mongo_model, self.path_mongo_model)

        self._copyActions()

        self.domain = self.template.domain


    def _checkdef(self,actionmethod,content):
        a=ActionMethod(self,actionmethod,content)
        self.actionmethods[actionmethod]=a

    def _copyActions(self):
        out="""
        from JumpScale import j

        ActionMethodDecorator=j.atyourservice.getActionMethodDecorator()
        class actionmethod(ActionMethodDecorator):
            def __init__(self,*args,**kwargs):
                ActionMethodDecorator.__init__(self,*args,**kwargs)
                self.selfobjCode="service=j.atyourservice.getService(role='$(service.role)', instance='$(service.instance)', die=True);selfobj=service.actions;selfobj.service=service"

        class Actions():

        """
        out=j.data.text.strip(out)

        if j.sal.fs.exists(self.template.path_actions):
            content=j.sal.fs.fileGetContents(self.template.path_actions)
            inclass=False
            indef=False
            intype=""
            defcontent=""

            for line in content.split("\n"):

                if line.find("from JumpScale import")!=-1:
                    continue
                if line.startswith("ActionsBase"):
                    continue

                if inclass:
                    if line.startswith("class"):
                        break #there should be no 2nd class

                    linestrip=line.strip()
                    #now we need to look for defs

                    if indef:
                        #lets check we didn't get out of the def or property
                        if linestrip.startswith("@") or linestrip.startswith("def"):
                            indef=False
                            intype=""                            
                            self._checkdef(actionmethod,defcontent) #remember action
                            defcontent=""
                            actionmethod=""

                    if indef:
                        #we are in the definition or in the property now
                        out+="%s\n"%line
                        defcontent+="%s\n"%line

                    if linestrip.startswith("@property"):
                        intype="prop"
                        continue

                    if linestrip.startswith("@"):
                        continue #ignore other decorators

                    if linestrip.startswith("def"):
                        if intype!="prop":
                            intype="def"
                        if linestrip.startswith("def input"):
                            #rewrite input line to make sure is always right format
                            line="    def input(self,name,role,instance,serviceargs):"    
                            actionmethod="input"                    
                        elif line.find("(self)")==-1:
                            #now check format of def is ok
                            raise j.exceptions.RuntimeError("Error in template action: %s\n    there should be no arguments in def line:\n    %s"%(self,line))
                        else:
                            linestrip2=linestrip[3:].strip()
                            actionmethod=linestrip2.split("(")[0].strip()
                            line="    def %s(self):"%actionmethod

                        if intype=="prop":
                            out+="    @property\n"
                        else:
                            if actionmethod!="input":
                                out+="    @actionmethod()\n"
                        out+="%s\n"%line
                        indef=True
                        continue

                else:
                    #are before the class starts
                    if line.startswith("class"):
                        inclass=True
                        continue
                    out+="%s\n"%line


        actionmethodsRequired=["input","hrd","install","stop","start","monitor","halt","check_up",\
            "check_down","check_requirements","cleanup","data_export","data_import","uninstall","removedata"]

        for method in actionmethodsRequired:
            if method not in self.actionmethods:
                if method!="input":
                    out+="    @actionmethod()\n    def %s(self):\n        return True\n\n"%method
                else:
                    out+="    def input(self,name,role,instance,serviceargs):\n        return serviceargs\n\n"
                self._checkdef(method,"") #remember action

        j.sal.fs.writeFile(filename=self.path_actions,contents=out)


    def newInstance(self, instance="main", role='', args={}, path='', parent=None, consume="",originator=None,yaml=None):
        """
        """

        if parent is not None and instance == "main":
            instance = parent.instance

        instance = instance.lower()

        service = j.atyourservice.getService(role=self.role, instance=instance,die=False)


        if service!=None:
            print("NEWINSTANCE: Service instance %s!%s  exists." % (self.name, instance))
            service.args.update(args or {})  # needed to get the new args in
            service._recipe = self
            service.init()

        else:
            shortkey = "%s!%s" % (self.role, instance)

            if path:
                fullpath = path
            elif parent is not None:
                fullpath = j.sal.fs.joinPaths(parent.path, shortkey)
            else:
                ppath = j.sal.fs.joinPaths(j.atyourservice.basepath, "services")
                fullpath = j.sal.fs.joinPaths(ppath, shortkey)

            if j.sal.fs.isDir(fullpath):
                j.events.opserror_critical(msg='Service with same role ("%s") and of same instance ("%s") is already installed.\nPlease remove dir:%s it could be this is broken install.' % (self.role, instance, fullpath), category="ays.servicetemplate")

            service = Service(self, instance=instance, args=args, path=fullpath, parent=parent, originator=originator)

            j.atyourservice._services[service.shortkey]=service

            if not j.sal.fs.exists(self.template.path_hrd_schema):
                service.init(yaml=yaml)
            else:
                service.init()

            service.consume(consume)

        return service

    def downloadfiles(self):
        """
        this method download any required files for this recipe as defined in the template.hrd
        Use this method when building a service to have all the files ready to sandboxing

        @return list of tuples containing the source and destination of the files defined in the recipeitem
                [(src, dest)]
        """
        dirList = []
        # download
        for recipeitem in self.hrd_template.getListFromPrefix("web.export"):
            if "dest" not in recipeitem:
                j.events.opserror_critical(msg="could not find dest in hrditem for %s %s" % (recipeitem, self), category="ays.servicetemplate")

            fullurl = "%s/%s" % (recipeitem['url'],
                                 recipeitem['source'].lstrip('/'))
            dest = recipeitem['dest']
            dest = j.application.config.applyOnContent(dest)
            destdir = j.sal.fs.getDirName(dest)
            j.sal.fs.createDir(destdir)
            # validate md5sum
            if recipeitem.get('checkmd5', 'false').lower() == 'true' and j.sal.fs.exists(dest):
                remotemd5 = j.sal.nettools.download(
                    '%s.md5sum' % fullurl, '-').split()[0]
                localmd5 = j.data.hash.md5(dest)
                if remotemd5 != localmd5:
                    j.sal.fs.remove(dest)
                else:
                    continue
            elif j.sal.fs.exists(dest):
                j.sal.fs.remove(dest)
            j.sal.nettools.download(fullurl, dest)

        for recipeitem in self.hrd_template.getListFromPrefix("git.export"):
            if "platform" in recipeitem:
                if not j.core.platformtype.myplatform.checkMatch(recipeitem["platform"]):
                    continue

            # pull the required repo
            dest0 = j.atyourservice._getRepo(recipeitem['url'], recipeitem=recipeitem)
            src = "%s/%s" % (dest0, recipeitem['source'])
            src = src.replace("//", "/")
            if "dest" not in recipeitem:
                j.events.opserror_critical(msg="could not find dest in hrditem for %s %s" % (recipeitem, self), category="ays.servicetemplate")
            dest = recipeitem['dest']

            dest = j.application.config.applyOnContent(dest)
            src = j.application.config.applyOnContent(src)

            if "link" in recipeitem and str(recipeitem["link"]).lower() == 'true':
                # means we need to only list files & one by one link them
                link = True
            else:
                link = False

            if src[-1] == "*":
                src = src.replace("*", "")
                if "nodirs" in recipeitem and str(recipeitem["nodirs"]).lower() == 'true':
                    # means we need to only list files & one by one link them
                    nodirs = True
                else:
                    nodirs = False

                items = j.sal.fs.listFilesInDir(
                    path=src, recursive=False, followSymlinks=False, listSymlinks=False)
                if nodirs is False:
                    items += j.sal.fs.listDirsInDir(
                        path=src, recursive=False, dirNameOnly=False, findDirectorySymlinks=False)

                items = [(item, "%s/%s" % (dest, j.sal.fs.getshortkey(item)), link)
                         for item in items]
            else:
                items = [(src, dest, link)]

            out = []
            for src, dest, link in items:
                delete = recipeitem.get('overwrite', 'true').lower() == "true"
                if dest.strip() == "":
                    raise j.exceptions.RuntimeError(
                        "a dest in coderecipe cannot be empty for %s" % self)
                if dest[0] != "/":
                    dest = "/%s" % dest
                else:
                    if link:
                        if not j.sal.fs.exists(dest):
                            j.sal.fs.createDir(j.sal.fs.getParent(dest))
                            j.sal.fs.symlink(src, dest)
                        elif delete:
                            j.sal.fs.remove(dest)
                            j.sal.fs.symlink(src, dest)
                    else:
                        print(("copy: %s->%s" % (src, dest)))
                        if j.sal.fs.isDir(src):
                            j.sal.fs.createDir(j.sal.fs.getParent(dest))
                            j.sal.fs.copyDirTree(
                                src, dest, eraseDestination=False, overwriteFiles=delete)
                        else:
                            j.sal.fs.copyFile(
                                src, dest, True, overwriteFile=delete)
                out.append((src, dest))
                dirList.extend(out)

        return dirList

    def listInstances(self):
        """
        return a list of instance name for this template
        """
        services = j.atyourservice.findServices(domain=self.domain, name=self.name)
        return [service.instance for service in services]

    def upload2AYSfs(self, path):
        """
        tell the ays filesystem about this directory which will be uploaded to ays filesystem
        """
        j.tools.sandboxer.dedupe(path, storpath="/tmp/aysfs", name="md", reset=False, append=True)

    def __repr__(self):
        return "Recipe: %-15s (%s)" % (self.name,self.template.version)