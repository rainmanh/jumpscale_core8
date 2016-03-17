
from JumpScale import j

# decorator
from ActionDecorator import ActionDecorator

# module imports
from apps.CuisineMongoCluster import mongoCluster
from apps.CuisineSkyDns import SkyDns
from apps.CuisineCaddy import Caddy
from apps.CuisineAydoStor import AydoStor
from apps.CuisineSyncthing import Syncthing
from apps.CuisineRedis import Redis
from apps.CuisineMongodb import Mongodb
from apps.CuisineFs import Fs
from apps.CuisineEtcd import Etcd
from apps.CuisineController import Controller
from apps.CuisineCoreOs import Core
from apps.CuisineGrafana import Grafana
from apps.CuisineInfluxdb import Influxdb
from apps.CuisineVulcand import Vulcand
from apps.CuisineWeave import Weave


import time

"""
please ensure that the start and build methods are separate and
the build doesnt place anyfile outside opt as it will be used in aysfs mounted system
"""

class actionrun(ActionDecorator):
    def __init__(self, *args, **kwargs):
        ActionDecorator.__init__(self, *args, **kwargs)
        self.selfobjCode = "cuisine=j.tools.cuisine.getFromId('$id');selfobj=cuisine.apps"


class CuisineApps(object):

    def __init__(self, executor, cuisine):
        self.executor = executor
        self.cuisine = cuisine

        # imported properties
        self._mongocluster = None
        self._skydns = None
        self._caddy = None
        self._stor = None
        self._syncthing = None
        self._redis = None
        self._mongodb = None
        self._fs = None
        self._etcd = None
        self._controller = None
        self._grafana = None
        self._influxdb = None
        self._core = None
        self._vulcand = None
        self._weave = None


    @property
    def skydns(self):
        if self._skydns is None:
            self._skydns = SkyDns(self.executor, self.cuisine)
        return self._skydns

    @property
    def mongocluster(self):
        if self._mongocluster is None:
            self._mongocluster = mongoCluster
        return self._mongocluster

    @property
    def caddy(self):
        if self._caddy is None:
            self._caddy = Caddy(self.executor, self.cuisine)
        return self._caddy

    @property
    def stor(self):
        if self._stor is None:
            self._stor = AydoStor(self.executor, self.cuisine)
        return self._stor

    @property
    def syncthing(self):
        if self._syncthing is None:
            self._syncthing = Syncthing(self.executor, self.cuisine)
        return self._syncthing

    @property
    def redis(self):
        if self._redis is None:
            self._redis = Redis(self.executor, self.cuisine)
        return self._redis

    @property
    def mongodb(self):
        if self._mongodb is None:
            self._mongodb = Mongodb(self.executor, self.cuisine)
        return self._mongodb

    @property
    def fs(self):
        if self._fs is None:
            self._fs = Fs(self.executor, self.cuisine)
        return self._fs

    @property
    def etcd(self):
        if self._etcd is None:
            self._etcd = Etcd(self.executor, self.cuisine)
        return self._etcd

    @property
    def controller(self):
        if self._controller is None:
            self._controller = Controller(self.executor, self.cuisine)
        return self._controller

    @property
    def core(self):
        if self._core is None:
            self._core = Core(self.executor, self.cuisine)
        return self._core

    @property
    def grafana(self):
        if self._grafana is None:
            self._grafana = Grafana(self.executor, self.cuisine)
        return self._grafana

    @property
    def influxdb(self):
        if self._influxdb is None:
            self._influxdb = Influxdb(self.executor, self.cuisine)
        return self._influxdb

    @property
    def vulcand(self):
        if self._vulcand is None:
            self._vulcand = Vulcand(self.executor, self.cuisine)
        return self._vulcand

    @property
    def weave(self):
        if self._weave is None:
            self._weave = Weave(self.executor, self.cuisine)
        return self._

    def all(self, start=False, sandbox=False, stor_addr=None):
        self.cuisine.installerdevelop.pip()
        self.cuisine.installerdevelop.python()
        self.cuisine.installerdevelop.jumpscale8()
        self.mongodb(start=start)
        self.cuisine.portal.install(start=start)
        self.redis.build(start=start, force=True)
        self.core.build(start=start)
        self.syncthing.build(start=start)
        self.controller(start=start)
        self.fs.build(start=start)
        self.stor.build(start=start)
        self.etcd.build(start=start)
        self.caddy.build(start=start)
        # self.skydns.build(start=start)
        self.influxdb(start=start)
        self.weave(start=start)
        if sandbox:
            if not stor_addr:
                raise RuntimeError("Store address should be specified if sandboxing enable.")
            self.sandbox(stor_addr)

    def sandbox(self, stor_addr, python=True):
        """
        stor_addr : addr to the store you want to populate. e.g.: https://stor.jumpscale.org/storx
        python : do you want to sandbox python too ? if you have segfault after trying sandboxing python, re run with python=False
        """
        # jspython is generated during install,need to copy it back into /opt before sandboxing
        self.cuisine.core.file_copy('/usr/local/bin/jspython', '/opt/jumpscale8/bin')

        # clean lib dir to avoid segfault during sandboxing
        self.cuisine.core.dir_remove('%s/*' % self.cuisine.core.dir_paths['libDir'])
        self.cuisine.core.dir_ensure('%s' % self.cuisine.core.dir_paths['libDir'])
        self.cuisine.core.file_link('/usr/local/lib/python3.5/dist-packages/JumpScale', '%s/JumpScale' % self.cuisine.core.dir_paths['libDir'])
        self.cuisine.core.file_link("%s/github/jumpscale/jumpscale_portal8/lib/portal" % self.cuisine.core.dir_paths["codeDir"], "%s/portal" % self.cuisine.core.dir_paths['jsLibDir'])

        # start sandboxing
        cmd = "j.tools.cuisine.local.apps.dedupe(['/opt'], 'js8_opt', '%s', sandbox_python=%s)" % (stor_addr, python)
        self.cuisine.core.run('js "%s"' % cmd)
        url_opt = '%s/static/js8_opt.flist' % stor_addr

        return url_opt

    def _sandbox_python(self, python=True):
        print("START SANDBOX")
        if python:
            paths = []
            paths.append("/usr/lib/python3.5/")
            paths.append("/usr/local/lib/python3.5/dist-packages")
            paths.append("/usr/lib/python3/dist-packages")

            excludeFileRegex=["-tk/", "/lib2to3", "-34m-", ".egg-info"]
            excludeDirRegex=["/JumpScale", "\.dist-info", "config-x86_64-linux-gnu", "pygtk"]

            dest = j.sal.fs.joinPaths(self.cuisine.core.dir_paths['base'], 'lib')

            for path in paths:
                j.tools.sandboxer.copyTo(path, dest, excludeFileRegex=excludeFileRegex, excludeDirRegex=excludeDirRegex)

            if not j.sal.fs.exists("%s/bin/python" % self.cuisine.core.dir_paths['base']):
                j.sal.fs.copyFile("/usr/bin/python3.5", "%s/bin/python" % self.cuisine.core.dir_paths['base'])

        j.tools.sandboxer.sandboxLibs("%s/lib" % self.cuisine.core.dir_paths['base'], recursive=True)
        j.tools.sandboxer.sandboxLibs("%s/bin" % self.cuisine.core.dir_paths['base'], recursive=True)
        print("SANDBOXING DONE, ALL OK IF TILL HERE, A Segfault can happen because we have overwritten ourselves.")

    def dedupe(self, dedupe_path, namespace, store_addr, output_dir='/tmp/sandboxer', sandbox_python=True):
        self.cuisine.core.dir_remove(output_dir)

        if sandbox_python:
            self._sandbox_python()

        if not j.data.types.list.check(dedupe_path):
            dedupe_path = [dedupe_path]

        for path in dedupe_path:
            print("DEDUPE:%s" % path)
            j.tools.sandboxer.dedupe(path, storpath=output_dir, name=namespace, reset=False, append=True, excludeDirs=['/opt/code'])

        store_client = j.clients.storx.get(store_addr)
        files_path = j.sal.fs.joinPaths(output_dir, 'files')
        files = j.sal.fs.listFilesInDir(files_path, recursive=True)
        error_files = []
        for f in files:
            src_hash = j.data.hash.md5(f)
            print('uploading %s' % f)
            uploaded_hash = store_client.putFile(namespace, f)
            if src_hash != uploaded_hash:
                error_files.append(f)
                print("%s hash doesn't match\nsrc     :%32s\nuploaded:%32s" % (f, src_hash, uploaded_hash))

        if len(error_files) == 0:
            print("all uploaded ok")
        else:
            raise RuntimeError('some files didnt upload properly. %s' % ("\n".join(error_files)))

        metadataPath = j.sal.fs.joinPaths(output_dir, "md", "%s.flist" % namespace)
        print('uploading %s' % metadataPath)
        store_client.putStaticFile(namespace+".flist", metadataPath)

    def caddyConfig(self,sectionname,config):
        """
        config format see https://caddyserver.com/docs/caddyfile
        """
        raise RuntimeError("needs to be implemented")


    @actionrun(action=True)
    def installdeps(self):
        self.cuisine.installer.base()
        self.cuisine.golang.install()
        self.cuisine.pip.upgrade('pip')
        self.cuisine.pip.install('pytoml')
        self.cuisine.pip.install('pygo')
