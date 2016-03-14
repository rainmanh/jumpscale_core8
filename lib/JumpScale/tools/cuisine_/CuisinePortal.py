from JumpScale import j

from ActionDecorator import ActionDecorator
class actionrun(ActionDecorator):
    def __init__(self,*args,**kwargs):
        ActionDecorator.__init__(self,*args,**kwargs)
        self.selfobjCode="cuisine=j.tools.cuisine.getFromId('$id');selfobj=cuisine.portal"


class CuisinePortal(object):

    def __init__(self,executor,cuisine):
        self.executor = executor
        self.cuisine = cuisine
        self.portal_dir = self.cuisine.args_replace('$appDir/portals/')
        self.example_portal_dir = j.sal.fs.joinPaths(self.portal_dir, 'example')

    def install(self, minimal=False, start=True, mongodbip="127.0.0.1", mongoport=27017, influxip="127.0.0.1", influxport=8086, grafanaip="127.0.0.1", grafanaport=3000, login="", passwd=""):
        """
        grafanaip and port should be the external ip of the machine 
        """
        if not self.cuisine.isMac:
            self.cuisine.installerdevelop.jumpscale8()
            self.cuisine.pip.upgrade("pip")
        self.installDeps()
        self.getcode()
        self.linkCode(minimal=minimal)
        self.serviceconnect(mongodbip=mongodbip, mongoport=mongoport, influxip=influxip, influxport=influxport, grafanaip=grafanaip, grafanaport=grafanaport)
        if start:
            self.start()

    @actionrun(action=True)
    def installDeps(self):
        """
        make sure new env arguments are understood on platform
        """
        deps = """
        setuptools
        aioredis
        # argh
        bcrypt
        Beaker
        blinker
        blosc
        # Cerberus
        # certifi
        # cffi
        # click
        # credis
        # crontab
        # Cython
        decorator
        # docker-py
        # dominate
        # ecdsa
        eve
        eve_docs
        eve-mongoengine
        # Events
        # Flask
        # Flask-Bootstrap
        # Flask-PyMongo
        # gitdb
        gitlab3
        # GitPython
        greenlet
        # hiredis
        html2text
        # influxdb
        # ipdb
        # ipython
        # ipython-genutils
        itsdangerous
        Jinja2
        # marisa-trie
        MarkupSafe
        mimeparse
        mongoengine
        msgpack-python
        netaddr
        # paramiko
        # path.py
        pathtools
        # pexpect
        # pickleshare
        psutil
        # psycopg2
        # ptyprocess
        # pycparser
        # pycrypto
        # pycurl
        # pygo
        # pygobject
        pylzma
        pymongo
        pystache
        # python-apt
        python-dateutil
        pytoml
        pytz
        PyYAML
        # pyzmq
        # redis
        # reparted
        requests
        simplegeneric
        simplejson
        six
        # smmap
        # SQLAlchemy
        traitlets
        ujson
        # unattended-upgrades
        urllib3
        visitor
        watchdog
        websocket
        websocket-client
        Werkzeug
        wheel
        # zmq
        """

        self.cuisine.pip.multiInstall(deps)
        self.changeEve()


    @actionrun(action=True)
    def getcode(self):
        self.cuisine.git.pullRepo("https://github.com/Jumpscale/jumpscale_portal8.git")


    @actionrun(action=True)
    def linkCode(self, minimal=False):
        self.cuisine.bash.environSet("LC_ALL", "C.UTF-8")
        destjslib = self.cuisine.run("js 'print(j.do.getPythonLibSystem(jumpscale=False))'", showout=False)

        self.cuisine.file_link("%s/github/jumpscale/jumpscale_portal8/lib/portal" % self.cuisine.dir_paths["codeDir"], "%s/portal" % destjslib, symbolic=True, mode=None, owner=None, group=None)
        self.cuisine.file_link("%s/github/jumpscale/jumpscale_portal8/lib/portal" % self.cuisine.dir_paths["codeDir"], "%s/portal" % self.cuisine.dir_paths['jsLibDir'])

        self.cuisine.run("js 'j.application.reload()'", showout=False, die=False)

        if not self.portal_dir.endswith("/"):
            self.portal_dir +='/'
        self.cuisine.dir_ensure(self.portal_dir)
        self.cuisine.file_link("%s/github/jumpscale/jumpscale_portal8/jslib" % self.cuisine.dir_paths["codeDir"], '%s/jslib' % self.portal_dir)
        self.cuisine.dir_ensure(j.sal.fs.joinPaths(self.portal_dir, 'portalbase'))
        self.cuisine.file_link("%s/github/jumpscale/jumpscale_portal8/apps/portalbase/system" %
                         self.cuisine.dir_paths["codeDir"],  '%s/portalbase/system' % self.portal_dir)
        self.cuisine.file_link("%s/github/jumpscale/jumpscale_portal8/apps/portalbase/wiki" %
                         self.cuisine.dir_paths["codeDir"], '%s/portalbase/wiki' % self.portal_dir)
        self.cuisine.file_link("%s/github/jumpscale/jumpscale_portal8/apps/portalbase/macros" %
                         self.cuisine.dir_paths["codeDir"], '%s/portalbase/macros' % self.portal_dir)
        self.cuisine.file_link("%s/github/jumpscale/jumpscale_portal8/apps/portalbase/templates" %
                         self.cuisine.dir_paths["codeDir"], '%s/portalbase/templates' % self.portal_dir)

        self.cuisine.dir_ensure(self.example_portal_dir)

        if not minimal:
            for space in self.cuisine.fs_find("%s/github/jumpscale/jumpscale_portal8/apps/gridportal/base" % self.cuisine.dir_paths["codeDir"],recursive=False):
                spacename = j.sal.fs.getBaseName(space)
                if not spacename == 'home':
                    self.cuisine.dir_ensure(j.sal.fs.joinPaths(self.example_portal_dir, 'base', 'gridportal'))
                    self.cuisine.file_link(space, j.sal.fs.joinPaths(self.example_portal_dir, 'base', 'gridportal', spacename))

        self.cuisine.dir_ensure('%s/base/home/.space' %self.example_portal_dir)
        self.cuisine.file_ensure('%s/base/home/home.md' %self.example_portal_dir)

        self.cuisine.dir_ensure('$tmplsDir/cfg/portal')
        self.cuisine.file_copy(j.sal.fs.joinPaths(self.cuisine.dir_paths["codeDir"], 'github/jumpscale/jumpscale_portal8/apps/portalbase/config.hrd'), '$tmplsDir/cfg/portal/config.hrd')

        self.cuisine.file_copy(j.sal.fs.joinPaths(self.cuisine.dir_paths["codeDir"], 'github/jumpscale/jumpscale_portal8/apps/portalbase/portal_start.py'), self.example_portal_dir)
        content = self.cuisine.file_read(j.sal.fs.joinPaths(self.cuisine.dir_paths["codeDir"], 'github/jumpscale/jumpscale_portal8/apps/portalbase/config.hrd'))
        configHRD = j.data.hrd.get(content=content, prefixWithName=False)
        configHRD.set('param.cfg.appdir', j.sal.fs.joinPaths(self.portal_dir, 'portalbase'))
        self.cuisine.file_write(j.sal.fs.joinPaths(self.example_portal_dir,'config.hrd'), content=str(configHRD))
        self.cuisine.file_copy("%s/jslib/old/images" % self.portal_dir, "%s/jslib/old/elfinder" % self.portal_dir, recursive=True)

    @actionrun(action=True)
    def serviceconnect(self, mongodbip="127.0.0.1", mongoport=27017, influxip="127.0.0.1", influxport=8086, grafanaip="127.0.0.1", grafanaport=3000):
        dest = j.sal.fs.joinPaths(self.cuisine.dir_paths['varDir'],'cfg', "portals")
        dest_cfg = j.sal.fs.joinPaths(dest, 'example', 'config.hrd')
        self.cuisine.dir_ensure(dest)
        content = self.cuisine.file_read('$tmplsDir/cfg/portal/config.hrd')
        tmp = j.sal.fs.getTempFileName()
        hrd = j.data.hrd.get(content=content, path=tmp)
        hrd.set('param.mongoengine.connection', {'host': mongodbip, 'port': mongoport})
        hrd.set('param.cfg.influx', {'host': influxip, 'port': influxport})
        hrd.set('param.cfg.grafana', {'host': grafanaip, 'port': grafanaport})
        hrd.save()
        self.cuisine.file_write(dest_cfg, str(hrd))
        j.sal.fs.remove(tmp)

    @actionrun(action=True)
    def changeEve(self):
        path = self.cuisine.run("js 'print(j.do.getPythonLibSystem(jumpscale=False))'")
        path = j.sal.fs.joinPaths(path, "eve_docs", "config.py")
        if not self.cuisine.file_exists(path):
            raise RuntimeError("Cannot find:%s, to convert to python 3"%path)
        self.cuisine.run("2to3-3.5 -f all -w %s" % path)

    @actionrun(action=True)
    def start(self):
        dest_dir = j.sal.fs.joinPaths(self.cuisine.dir_paths['varDir'],'cfg')
        cfg_path = j.sal.fs.joinPaths(dest_dir, 'portals/example/config.hrd')
        app_dir = j.sal.fs.joinPaths(dest_dir, 'portals/portalbase')

        self.cuisine.file_copy(self.portal_dir, dest_dir, recursive=True, overwrite=True)

        content = self.cuisine.file_read(cfg_path)
        hrd = j.data.hrd.get(content=content, prefixWithName=False)
        hrd.set('param.cfg.appdir', app_dir)
        self.cuisine.file_write(cfg_path, str(hrd))

        cmd = "cd %s; jspython portal_start.py" % j.sal.fs.joinPaths(dest_dir, 'portals/example')
        self.cuisine.tmux.createSession("portal", ['portal'])
        self.cuisine.tmux.executeInScreen('portal', 'portal', cmd=cmd)
