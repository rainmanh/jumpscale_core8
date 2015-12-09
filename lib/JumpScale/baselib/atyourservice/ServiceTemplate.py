

from JumpScale import j
import imp
import sys
import os

import JumpScale.baselib.actions

from Service import *

from ServiceTemplateBuilder import *


def loadmodule(name, path):
    parentname = ".".join(name.split(".")[:-1])
    sys.modules[parentname] = __package__
    mod = imp.load_source(name, path)
    return mod


class ServiceTemplate(object):

    def __init__(self, path, domain=""):
        self.path = path
        # self._path_actions_py = j.sal.fs.joinPaths(self.path, 'actions_tmpl.py')
        self.path_hrd_template = j.sal.fs.joinPaths(self.path, "service.hrd")
        self.path_hrd_instance = j.sal.fs.joinPaths(self.path, "instance.hrd")

        base = j.sal.fs.getBaseName(path)

        _, self. name, self.version, _, _ = j.atyourservice.parseKey(base)
        if base.find("__") != -1:
            self.domain, self.name = base.split("__", 1)
        else:
            self.domain = domain
        self.role = self.name.split('.')[0]
        self.key = j.atyourservice.getKey(self)

        self._hrd = None
        self._hrd_instance = None

        self._actions = None

        self.builder = ServiceTemplateBuilder()

    def _path_action(self, actionType):
        return j.sal.fs.joinPaths(self.path, "%s.py" % actionType)

    @property
    def hrd_template(self):
        if self._hrd:
            return self._hrd
        hrdpath = self.path_hrd_template
        if not j.sal.fs.exists(hrdpath):
            # check if we can find it in other ays template
            if self.name.find(".") != -1:
                name = self.name.split(".", 1)[0]
                templ = j.atyourservice.getTemplate(self.domain, name, die=False)
                if templ is not None:
                    self._hrd = templ.hrd_template
                    self.path_hrd_template = templ.path_hrd_template
                    return self._hrd
            j.events.opserror_critical(msg="can't find %s." % hrdpath, category="ays load hrd template")
        else:
            self._hrd = j.data.hrd.get(hrdpath, prefixWithName=False)
        return self._hrd

    @property
    def hrd_instance(self):
        if self._hrd_instance:
            return self._hrd_instance
        hrdpath = self.path_hrd_instance
        if not j.sal.fs.exists(hrdpath):
            # check if we can find it in other ays instance
            if self.name.find(".") != -1:
                name = self.name.split(".", 1)[0]
                templ = j.atyourservice.getTemplate(self.domain,name,die=False)
                if templ is not None:
                    self._hrd_instance = templ.hrd_instance
                    self.path_hrd_instance = templ.path_hrd_instance
                    return self._hrd_instance
            j.events.opserror_critical(msg="can't find %s." % hrdpath, category="ays load hrd instance")
        else:
            self._hrd_instance = j.data.hrd.get(hrdpath, prefixWithName=False)
        return self._hrd_instance

    @property
    def path_actions_mgmt(self):
        return self._path_action("actions_mgmt")

    @property
    def path_actions_node(self):
        return self._path_action("actions_node")

    @property
    def path_actions_tmpl(self):
        return self._path_action("actions_tmpl")
        # actionPy = self._path_actions_py
        # if j.sal.fs.exists(actionPy):
        #     self._path_actions_py = actionPy
        # else:
        #     # check if we can find it in other ays template
        #     if self.name.find(".")!=-1:
        #         name=self.name.split(".",1)[0]
        #         templ=j.atyourservice.getTemplate(self.domain,name,die=False)
        #         if templ!=None:
        #             self._actions=templ.actions
        #             self._path_actions_py=templ.path_actions_py
        # return self._path_actions_py

    def newInstance(self, instance="main", args={}, path='', parent=None, consume="",originator=None):
        """
        """
        self.actions  # DO NOT REMOVE

        if parent is not None and instance == "main":
            instance = parent.instance

        instance = instance.lower()

        services = j.atyourservice.findServices(name=self.name, domain=self.domain, version=self.version,instance=instance, parent=parent)

        if len(services) == 1:
            if j.application.debug:
                print("Service %s|%s!%s  exists." % (self.domain, self.name, instance))

            services[0].args.update(args)  # needed to get the new args in
            services[0]._servicetemplate = self
            service = services[0]

        elif len(services) > 1:
            raise RuntimeError("Found too many ayses for %s!%s for parent %s "%(self.name,instance,parent))

        else:
            name9 = self.name.split(".")[0]
            basename = "%s!%s" % (name9, instance)
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
                if j.sal.fs.exists(path=j.sal.fs.joinPaths(fullpath, "instance_.hrd")):
                    j.sal.fs.removeDirTree(fullpath)
                else:
                    j.events.opserror_critical(msg='Service with same role ("%s") and of same instance ("%s") is already installed.\nPlease remove dir:%s it could be this is broken install.' % (name9, instance, fullpath), category="ays.servicetemplate")

            service = Service(self, instance=instance, args=args, path=fullpath, parent=parent,originator=originator)
            if service not in j.atyourservice.services:
                j.atyourservice.services.append(service)

            # will call apply
            service.init()

            if consume != "":
                if j.core.types.list.check(consume):
                    for serv in consume:
                        service.consume(serv)
                else:
                    service.consume(consume)

        return service

    def listInstances(self):
        """
        return a list of instance name for this template
        """
        services = j.atyourservice.findServices(domain=self.domain, name=self.name)
        return [service.instance for service in services]

    @property
    def actions(self):
        if self._actions is None:
            self._loadActions()
        return self._actions

    def _loadActions(self):
        if self._actions is not None:
            return
        actionPy = self.path_actions_tmpl
        if j.sal.fs.exists(actionPy):
            self.hrd_template.applyOnFile(actionPy)
            j.application.config.applyOnFile(actionPy)
            modulename = "JumpScale.atyourservice.%s.%s" % (self.domain, self.name)
            mod = loadmodule(modulename, actionPy)
            self._actions = mod.Actions()
        else:
            self._actions = j.atyourservice.getActionsBaseClassTmpl()()
        #@todo rewrite for inheritence


        # else:
        #     # check if we can find it in other ays template
        #     if self.name.find(".")!=-1:
        #         name=self.name.split(".",1)[0]
        #         templ=j.atyourservice.getTemplate(self.domain,name,die=False)
        #         if templ!=None:
        #             self._actions=templ.actions
        #             self._path_actions_py=templ.path_actions_py
        #             return
        #     j.events.opserror_critical(msg="can't find %s." % actionPy, category="ays loadActions")

    def build(self, build_server=None, image_build=False, image_push=False,debug=True,syncLocalJumpscale=False):
        """
        build_server : node service where the the service will be build
        """
        log("build")


        if debug:
            syncLocalJumpscale=True

        if build_server is None:
            self.actions.build(self)
            return

        build_host = None
        if j.core.types.string.check(build_server):
            domain, name, version, instance, role = j.atyourservice.parseKey(build_server)
            build_host = j.atyourservice.getService(domain=domain, name=name, instance=instance, role=role)
        else:
            build_host = build_server

        build_info = self.hrd_template.getDict('build')
        image = build_info['image']
        repo = build_info['repo']
        if 'dedupe_ns' in build_info:
            dedupe_ns = build_info['dedupe_ns']
        else:
            dedupe_ns = "dedupe"

        error=""

        try:
            # make sure to clean old service that could still be in the ays_repo
            j.atyourservice.remove(name='docker_build', instance=self.name)

            data = {
                'docker.build.repo': repo,
                'docker.image': image,
                'docker.build': image_build,
                'docker.upload': image_push,
            }
            print("init docker_build")
            docker_build = j.atyourservice.new(name='docker_build', instance=self.name, args=data, parent=build_host)

            print("deploy docker on build server %s" % build_host)
            j.atyourservice.apply()  # deploy docker in build server

            docker_addr = docker_build.hrd.getStr("tcp.addr")
            docker_port = docker_build.hrd.getStr("ssh.port")

            # remove key from know hosts, cause this is liklely that the key will change at each build because
            # we hit a newly created docker container each time.
            j.do.execute('ssh-keygen -f "/root/.ssh/known_hosts" -R [%s]:%s' % (docker_addr, docker_port))

            dockerExecutor = j.tools.executor.getSSHBased(docker_addr, docker_port)
            # clean service tempates in docker to be sure we have the local version.
            if dockerExecutor.cuisine.dir_exists(self.path):
                dockerExecutor.cuisine.dir_remove(self.path, recursive=True)
            # upload local template inside the docker.
            dockerExecutor.upload(self.path, self.path)

            if syncLocalJumpscale:
                print ("upload jumpscale core lib to build docker.")
                dockerExecutor.upload("/opt/code/github/jumpscale/jumpscale_core8/lib/","/opt/code/github/jumpscale/jumpscale_core8/lib/")

            print("start build of %s" % self)
            dockerExecutor.execute("ays build -n %s" % self.name)

            # push metadata and flist to stores
            for client in j.atyourservice.findServices(name='ays_stor_client.ssh'):
                if client.hrd.exists('tcp.addr'):
                    ip = client.hrd.getStr('tcp.addr')
                else:
                    ip = client.hrd.getStr('ip')

                store_path = client.hrd.getStr('root')
                store_path = j.tools.path.get(store_path).joinpath(dedupe_ns)
                dest = "%s:%s" % (ip, store_path)
                # dockerExecutor.execute('mkdir -p %s' % store_path)

                cmd = 'rsync -rP /tmp/aysfs/files/ %s' % dest
                print('push metadata and flist to %s' % dest)
                dockerExecutor.execute(cmd)

            print('download flist file back into template directory')
            dockerExecutor.download("/tmp/aysfs/md/*", self.path)
        except Exception as e:
            error=j.errorconditionhandler.parsePythonErrorObject(e)
            eco.getBacktraceDetailed()
        finally:
            if debug==False:
                docker_build.stop()
                docker_build.removedata()
                j.atyourservice.remove(name=docker_build.name, instance=docker_build.instance)
            if error!="":
                error="Could not build:%s\n%s"%(self,error)
                j.events.opserror_critical(error,"ays.build")


    def installRecipe(self):
        """
        this method download any required files for this template and put it at the location defined in the recipes.
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

                items = j.do.listFilesInDir(
                    path=src, recursive=False, followSymlinks=False, listSymlinks=False)
                if nodirs is False:
                    items += j.do.listDirsInDir(
                        path=src, recursive=False, dirNameOnly=False, findDirectorySymlinks=False)

                items = [(item, "%s/%s" % (dest, j.do.getBaseName(item)), link)
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
                            j.sal.fs.createDir(j.do.getParent(dest))
                            j.do.symlink(src, dest)
                        elif delete:
                            j.do.delete(dest)
                            j.do.symlink(src, dest)
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

    def upload2AYSfs(self, path):
        """
        tell the ays filesystem about this directory which will be uploaded to ays filesystem
        """
        j.tools.sandboxer.dedupe(path, storpath="/tmp/aysfs", name="md", reset=False, append=True)

    def __repr__(self):
        return "%-15s:%s (%s)" % (self.domain, self.name,self.version)

    def __str__(self):
        return self.__repr__()
