from JumpScale import j

# import JumpScale.baselib.actions

from ServiceTemplate import ServiceTemplate


from Service import Service, loadmodule
# from inspect import getmembers, isfunction, isclass, getsource

DECORATORCODE = """
ActionMethodDecorator=j.atyourservice.getActionMethodDecorator()
class action(ActionMethodDecorator):
    def __init__(self,*args,**kwargs):
        ActionMethodDecorator.__init__(self,*args,**kwargs)
        self.selfobjCode="service=j.atyourservice._currentService;selfobj=service.recipe.actions;selfobj.service=service"

"""


class ActionMethod():

    def __init__(self, recipe, defline="", name=""):
        if name == "":
            line = defline.strip()[4:]
            name = line.split("(", 1)[0].strip()
        self.defline = defline
        self.source = ""
        self.name = name
        self.hash = ""
        self.recipe = recipe
        self.hrdArgKeys = []  # names of arguments as used in hrd which are used in this action method

    def _process(self):
        if self.source != "":
            self.hash = j.data.hash.md5_string(self.source)

            #need to make sure we are not using templ var's in these 2 methods because they get executed before we can apply the hrd arguments
            if self.name in ["input","init"]:
                if self.source.find("$(")!=-1:
                    raise j.exceptions.Input("Action method:%s should not have template variable '$(...' in sourcecode for init or input method."%(self))

        # for now we don't do a check, later want to make sure we don't call other services, now we just put impact on all hrd schema arguments
        self.recipe.schema
        # for now we take all arguments, later we need to be more specific
        self.hrdArgKeys = [item for item in self.recipe.schema.items.keys()]

    def __repr__(self):
        return "actionmethod: %s:%s" % (self.recipe,self.name)

    __str__ = __repr__


class ServiceRecipe(ServiceTemplate):

    def __init__(self, path="", template=None, aysrepopath=""):

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
            self.path = j.sal.fs.joinPaths(aysrepopath, "recipes", template.name)
            self.name = template.name
            self.template = template
        self.domain = self.template.domain

        # copy the files
        if not j.sal.fs.exists(path=self.path):
            firstime = True
            j.sal.fs.createDir(self.path)
        else:
            firstime = False

        self._action_methods = None

        self.actionmethods = {}

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

    def _copyActions(self):
        self._out = ""

        actionmethodsRequired = ["input", "init", "install", "stop", "start", "monitor", "halt", "check_up", "check_down",
                                 "check_requirements", "cleanup", "data_export", "data_import", "uninstall", "removedata", "change"]

        if j.sal.fs.exists(self.template.path_actions):
            content = j.sal.fs.fileGetContents(self.template.path_actions)
        else:
            content = "class Actions():\n\n"

        if content.find("class action(ActionMethodDecorator)") != -1:
            raise j.exceptions.Input("There should be no decorator specified in %s" % self.path_actions)

        content = "%s\n\n%s" % (DECORATORCODE, content)

        content = content.replace("from JumpScale import j", "")
        content = "from JumpScale import j\n\n%s" % content

        state = "INIT"
        am = None

        # DO NOT CHANGE TO USE PYTHON PARSING UTILS
        lines = content.splitlines()
        size = len(lines)
        i = 0
        while i < size:
            line = lines[i]
            linestrip = line.strip()
            if state == "INIT" and linestrip.startswith("class Actions"):
                state = "MAIN"
                i += 1
                continue

            if state == "MAIN" and linestrip.startswith("@"):
                if am is not None:
                    am._process()
                    am = None
                i += 1
                continue

            if state == "MAIN" and linestrip.startswith("def"):
                if am is not None:
                    am._process()
                am = ActionMethod(self, defline=line)
                self.actionmethods[am.name] = am

                # make sure the required method have the action() decorator
                if am.name in actionmethodsRequired and not lines[i-1].strip().startswith('@'):
                    lines.insert(i, '\n    @action()')
                    size += 1

                i += 1
                continue

            if am is not None:
                am.source += "%s\n" % line[8:]
            i += 1

        content = '\n'.join(lines)

        # process the last actionmethod
        if am is not None:
            am._process()

        # add missing methods
        for actionname in actionmethodsRequired:
            if actionname not in self.actionmethods:
                am = ActionMethod(self, name=actionname)
                am._process()
                self.actionmethods[am.name] = am
                #not found
                if actionname == "input":
                    content += '\n\n    def input(self,name,role,instance,serviceargs):\n        return serviceargs\n'
                elif actionname == "change":
                    content += '\n\n    def change(self,stateitem):\n        return True\n'
                else:
                    content += "\n\n    @action()\n    def %s(self):\n        return True\n" % actionname

        j.sal.fs.writeFile(self.path_actions, content)

    @property
    def actions(self):
        if self._action_methods is None:
            print("reload mgmt actions for %s" % (self))
            modulename = "JumpScale.atyourservice.%s.%s" % (self.domain, self.name)
            mod = loadmodule(modulename, self.path_actions)
            self._action_methods = mod.Actions()

        return self._action_methods

    def newInstance(self, instance="main", role='', args={}, path='', parent=None, consume="", originator=None, yaml=None):
        """
        """

        if parent is not None and instance == "main":
            instance = parent.instance

        instance = instance.lower()

        service = j.atyourservice.getService(role=self.role, instance=instance, die=False)

        if service is not None:
            print("NEWINSTANCE: Service instance %s!%s  exists." % (self.name, instance))
            service.args.update(args or {})  # needed to get the new args in
            service._recipe = self
            service.init()

        else:
            key = "%s!%s" % (self.role, instance)

            if path:
                fullpath = path
            elif parent is not None:
                fullpath = j.sal.fs.joinPaths(parent.path, key)
            else:
                ppath = j.sal.fs.joinPaths(j.atyourservice.basepath, "services")
                fullpath = j.sal.fs.joinPaths(ppath, key)

            if j.sal.fs.isDir(fullpath):
                j.events.opserror_critical(msg='Service with same role ("%s") and of same instance ("%s") is already installed.\nPlease remove dir:%s it could be this is broken install.' % (self.role, instance, fullpath))

            service = Service(self, instance=instance, args=args, path=fullpath, parent=parent, originator=originator)

            j.atyourservice._services[service.key] = service

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

                raise RuntimeError("getshort_key does not even exist")
                items = [(item, "%s/%s" % (dest, j.sal.fs.getshort_key(item)), link)
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
        return "Recipe: %-15s (%s)" % (self.name, self.template.version)
