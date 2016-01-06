

from JumpScale import j

# import JumpScale.baselib.actions

from ServiceTemplate import ServiceTemplate
from Service import Service


class ServiceRecipe(ServiceTemplate):

    def __init__(self, path="",template=None,aysrepopath=""):

        if aysrepopath=="" or aysrepopath==None:
            aysrepopath=j.dirs.amInAYSRepo()

        if aysrepopath=="" or aysrepopath==None:
            raise RuntimeError("A service instance can only be used when used from a ays repo")

        if path!="":
            if not j.sal.fs.exists(path):
                raise RuntimeError("Could not find path for recipe")
            self.path=path
            name=self.state.hrd.get("template.name")
            domain=self.state.hrd.get("template.domain")
            version=self.state.hrd.get("template.version")
            self.parent=j.atyourservice.getTemplate(domain=domain, name=name, version=version)
            self.name=self.parent.name
        else:
            self.path = j.sal.fs.joinPaths(aysrepopath,"recipes",template.name)
            self.name=template.name
            self.parent=template

        #copy the files
        if not j.sal.fs.exists(path=self.path):
            firstime=True
            j.sal.fs.createDir(self.path)
        else:
            firstime=False

        self._init()

        if j.sal.fs.exists(self.parent.path_hrd_template):
            j.sal.fs.copyFile(self.parent.path_hrd_template,self.path_hrd_template)
        if j.sal.fs.exists(self.parent.path_hrd_schema):
            j.sal.fs.copyFile(self.parent.path_hrd_schema,self.path_hrd_schema)
        if j.sal.fs.exists(self.parent.path_actions_mgmt):
            j.sal.fs.copyFile(self.parent.path_actions_mgmt,self.path_actions_mgmt)
        if j.sal.fs.exists(self.parent.path_actions_node):
            j.sal.fs.copyFile(self.parent.path_actions_node,self.path_actions_node)

        self._state=None
        # if firstime:
        #     self.state.save()

        self.domain=self.parent.domain


    @property
    def state(self):
        """
        """
        if self._state is None:
            self._state=None
        return self._state        

    def newInstance(self, instance="main", args={}, path='', parent=None, consume="",originator=None):
        """
        """
        self.actions  # DO NOT REMOVE

        if parent is not None and instance == "main":
            instance = parent.instance

        instance = instance.lower()

        services = j.atyourservice.findServices(role=self.role, instance=instance)

        if len(services) == 1:
            if j.application.debug:
                print("Service instance %s!%s  exists." % (self.name, instance))

            services[0].args.update(args)  # needed to get the new args in
            services[0]._recipe = self
            service = services[0]

            service.init()

        elif len(services) > 1:
            raise RuntimeError("Found too many ays'es for %s!%s for parent %s "%(self.name,instance,parent))

        else:
            basename = "%s!%s" % (self.role, instance)

            if path != "" and path is not None:
                fullpath = path
            elif parent is not None:
                fullpath = j.sal.fs.joinPaths(parent.path, basename)
            else:
                ppath = j.dirs.amInAYSRepo()
                if ppath is None:
                    ppath = "/etc/ays/local/"
                else:
                    ppath = "%s/services/" % (ppath)
                fullpath = j.sal.fs.joinPaths(ppath, basename)

            if j.sal.fs.isDir(fullpath):
                j.events.opserror_critical(msg='Service with same role ("%s") and of same instance ("%s") is already installed.\nPlease remove dir:%s it could be this is broken install.' % (self.role, instance, fullpath), category="ays.servicetemplate")

            service = Service(self, instance=instance, args=args, path=fullpath, parent=parent,originator=originator)


            if service not in j.atyourservice.services:
                j.atyourservice.services.append(service)

            service.init()

            if consume != "":
                if j.data.types.list.check(consume):
                    for serv in consume:
                        service.consume(serv)
                else:
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
                localmd5 = j.tools.hash.md5(dest)
                if remotemd5 != localmd5:
                    j.sal.fs.remove(dest)
                else:
                    continue
            elif j.sal.fs.exists(dest):
                j.sal.fs.remove(dest)
            j.sal.nettools.download(fullurl, dest)

        for recipeitem in self.hrd_template.getListFromPrefix("git.export"):
            if "platform" in recipeitem:
                if not j.core.platformtype.checkMatch(recipeitem["platform"]):
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

                items = [(item, "%s/%s" % (dest, j.sal.fs.getBaseName(item)), link)
                         for item in items]
            else:
                items = [(src, dest, link)]

            out = []
            for src, dest, link in items:
                delete = recipeitem.get('overwrite', 'true').lower() == "true"
                if dest.strip() == "":
                    raise RuntimeError(
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
        return "Recipe: %-15s (%s)" % (self.name,self.parent.version)
