

from JumpScale import j
import imp
import sys
import os

import JumpScale.baselib.actions

from Service import *

# from ServiceTemplateBuilder import *


def loadmodule(name, path):
    parentname = ".".join(name.split(".")[:-1])
    sys.modules[parentname] = __package__
    mod = imp.load_source(name, path)
    return mod


class ServiceTemplate(object):

    def __init__(self, path,domain=""):
        self.path = path

        base = j.sal.fs.getBaseName(path)

        _, self.name, self.version, _, _ = j.atyourservice.parseKey(base)
        if base.find("__") != -1:
            self.domain, self.name = base.split("__", 1)
        else:
            self.domain = domain

        self._init()
        self.key = j.atyourservice.getKey(self)

    def _init(self):
        self.path_hrd_template = j.sal.fs.joinPaths(self.path, "template.hrd")
        self.path_hrd_schema = j.sal.fs.joinPaths(self.path, "schema.hrd")
        self.path_actions_mgmt = j.sal.fs.joinPaths(self.path, "actions_mgmt.py")
        self.path_actions_node = j.sal.fs.joinPaths(self.path, "actions_node.py")

        self.role = self.name.split('.')[0]

        self._hrd = None
        self._schema = None
        self._actions = None

    @property
    def hrd(self):
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
            self._hrd=j.data.hrd.get(content="")
            # j.events.opserror_critical(msg="can't find %s." % hrdpath, category="ays load hrd template")
        else:
            self._hrd = j.data.hrd.get(hrdpath, prefixWithName=False)
        return self._hrd

    @property
    def schema(self):
        if self._schema:
            return self._schema
        hrdpath = self.path_hrd_schema
        if not j.sal.fs.exists(hrdpath):
            # check if we can find it in other ays instance
            if self.name.find(".") != -1:
                name = self.name.split(".", 1)[0]
                templ = j.atyourservice.getTemplate(self.domain,name,die=False)
                if templ is not None:
                    self._schema = templ.hrd_schema
                    self.path_hrd_schema = templ.path_hrd_schema
                    return self._schema
            j.events.opserror_critical(msg="can't find %s." % hrdpath, category="ays load hrd instance")
        else:
            self._schema = j.data.hrd.getSchema(hrdpath)
        return self._schema

    @property
    def actions(self):
        if self._actions is None:
            if j.sal.fs.exists(self.path_actions_mgmt):
                if self.domain=="ays":
                    self.hrd.applyOnFile(self.path_actions_mgmt)
                    j.application.config.applyOnFile(self.path_actions_mgmt)
                modulename = "JumpScale.atyourservice.%s.%s.template" % (self.domain, self.name)
                mod = loadmodule(modulename, self.path_actions_mgmt)
                self._actions = mod.Actions()
            else:
                self._actions=j.atyourservice.getActionsBaseClassMgmt()
        return self._actions

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
        if j.data.types.string.check(build_server):
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

    @property
    def recipe(self):
        from ServiceRecipe import ServiceRecipe
        return ServiceRecipe(template=self)

    def __repr__(self):
        return "template: %-15s:%s (%s)" % (self.domain, self.name,self.version)

    def __str__(self):
        return self.__repr__()
