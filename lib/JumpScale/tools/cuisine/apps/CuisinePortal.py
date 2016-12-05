from JumpScale import j
import time


base = j.tools.cuisine._getBaseClass()


class CuisinePortal(base):

    def __init__(self, executor, cuisine):
        self._executor = executor
        self._cuisine = cuisine
        self._config = None
        self.portal_dir = j.sal.fs.joinPaths(self._cuisine.core.dir_paths["appDir"], "portals/")
        self.main_portal_dir = j.sal.fs.joinPaths(self.portal_dir, 'main')
        self._cuisine.core.dir_ensure(self.main_portal_dir)
        self.cfg_path = j.sal.fs.joinPaths(self.main_portal_dir, 'config.hrd')

    def configure(self, mongodbip="127.0.0.1", mongoport=27017, influxip="127.0.0.1",
                  influxport=8086, grafanaip="127.0.0.1", grafanaport=3000):

        # go from template dir which go the file above
        content = self._cuisine.core.file_read('$tmplsDir/cfg/portal/config.hrd')

        hrd = j.data.hrd.get(content=content, prefixWithName=False)

        # ITS ALREADY THE DEFAULT IN THE CONFIG DIR
        # hrd.set('param.cfg.appdir', j.sal.fs.joinPaths(self.portal_dir, 'portalbase'))

        hrd.set('param.mongoengine.connection', {'host': mongodbip, 'port': mongoport})
        hrd.set('param.cfg.influx', {'host': influxip, 'port': influxport})
        hrd.set('param.cfg.grafana', {'host': grafanaip, 'port': grafanaport})

        if "darwin" in self._cuisine.platformtype.osname:
            hrd.set('param.cfg.port', '8200')
        self._config = hrd

    def install(self, start=True, installdeps=False, branch='master'):
        """
        grafanaip and port should be the external ip of the machine
        Portal install will only install the portal and libs. No spaces but the system ones will be add by default.
        To add spaces and actors, please use addSpace and addactor
        """
        # set encoding to utf-8
        self._cuisine.bash.environSet("LC_ALL", "C.UTF-8")
        self._cuisine.bash.environSet("LANG", "C.UTF-8")

        # install the dependencies if required
        if installdeps:
            self.installDeps()

        # pull repo with required branch ; then link dirs and files in required places
        self.getcode(branch=branch)
        self.linkCode()

        if start:
            self.start()

    def installDeps(self):
        """
        make sure new env arguments are understood on platform
        """
        self._cuisine.development.pip.ensure()

        deps = """
        cffi==1.5.2
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
        mongoengine==0.10.6
        msgpack-python
        netaddr
        # paramiko
        # path.py
        pathtools
        # pexpect
        # pickleshare
        psutil
        pyjwt
        # psycopg2
        # ptyprocess
        # pycparser
        # pycrypto
        # pycurl
        # pygo
        # pygobject
        pylzma
        pymongo==3.2.1
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
        pillow
        gevent
        flask
        Flask-Bootstrap
        snakeviz
        """

        if not "darwin" in self._cuisine.platformtype.osname:
            self._cuisine.package.ensure('build-essential')
            self._cuisine.package.ensure('libssl-dev')
            self._cuisine.package.ensure('libffi-dev')
            self._cuisine.package.ensure('python3-dev')

        self._cuisine.development.pip.multiInstall(deps)

        if "darwin" in self._cuisine.platformtype.osname:
            self._cuisine.core.run("brew install libtiff libjpeg webp little-cms2")
            self._cuisine.core.run("brew install snappy")
            self._cuisine.core.run('CPPFLAGS="-I/usr/local/include -L/usr/local/lib" pip3 install python-snappy')
        else:
            self._cuisine.package.multiInstall(['libjpeg-dev', 'libffi-dev', 'zlib1g-dev'])

        # snappy install
        if not "darwin" in self._cuisine.platformtype.osname:
            self._cuisine.package.ensure('libsnappy-dev')
            self._cuisine.package.ensure('libsnappy1v5')

        self._cuisine.development.pip.install('python-snappy')

    def getcode(self, branch='master'):
        self._cuisine.development.git.pullRepo(
            "https://github.com/Jumpscale/jumpscale_portal8.git", branch=branch)

    def linkCode(self):
        self._cuisine.bash.environSet("LC_ALL", "C.UTF-8")

        destjslib = self._cuisine.core.dir_paths['jsLibDir']

        # _, destjslib, _ = self._cuisine.core.run("js --quiet 'print(j.do.getPythonLibSystem(jumpscale=True))'",
        #                                          showout=False)
        #
        # if "darwin" in self._cuisine.platformtype.osname:
        #     # Needs refining,In osx destjslib='load dirs\n/usr/local/lib/python3.5/site-packages/JumpScale/'
        #     destjslib = destjslib.split("\n")[1]

        if self._cuisine.core.file_exists(destjslib):
            self._cuisine.core.file_link("%s/github/jumpscale/jumpscale_portal8/lib/portal" % self._cuisine.core.dir_paths["codeDir"],
                                         "%s/portal" % destjslib, symbolic=True, mode=None, owner=None, group=None)

        self._cuisine.core.run("js --quiet 'j.application.reload()'", showout=False, die=False)

        if not self.portal_dir.endswith("/"):
            self.portal_dir += '/'
        self._cuisine.core.dir_ensure(self.portal_dir)

        CODE_DIR = self._cuisine.core.dir_paths["codeDir"]
        self._cuisine.core.file_link("%s/github/jumpscale/jumpscale_portal8/jslib" % CODE_DIR,
                                     '%s/jslib' % self.portal_dir)
        self._cuisine.core.dir_ensure(j.sal.fs.joinPaths(self.portal_dir, 'portalbase'))
        self._cuisine.core.file_link("%s/github/jumpscale/jumpscale_portal8/apps/portalbase/system" % CODE_DIR,
                                     '%s/portalbase/system' % self.portal_dir)
        self._cuisine.core.file_link("%s/github/jumpscale/jumpscale_portal8/apps/portalbase/wiki" % CODE_DIR,
                                     '%s/portalbase/wiki' % self.portal_dir)
        self._cuisine.core.file_link("%s/github/jumpscale/jumpscale_portal8/apps/portalbase/macros" %
                                     CODE_DIR, '%s/portalbase/macros' % self.portal_dir)
        self._cuisine.core.file_link("%s/github/jumpscale/jumpscale_portal8/apps/portalbase/templates" %
                                     CODE_DIR, '%s/portalbase/templates' % self.portal_dir)

        self._cuisine.core.dir_ensure(self.main_portal_dir)

        self._cuisine.core.dir_ensure('%s/base/home/.space' % self.main_portal_dir)
        self._cuisine.core.file_ensure('%s/base/home/home.md' % self.main_portal_dir)

        self._cuisine.core.dir_ensure('$tmplsDir/cfg/portal')
        self._cuisine.core.file_copy(j.sal.fs.joinPaths(CODE_DIR, 'github/jumpscale/jumpscale_portal8/apps/portalbase/config.hrd'),
                                     '$tmplsDir/cfg/portal/config.hrd')

        # copy portal_start.py
        self._cuisine.core.file_copy(j.sal.fs.joinPaths(CODE_DIR, 'github/jumpscale/jumpscale_portal8/apps/portalbase/portal_start.py'),
                                     self.main_portal_dir)
        self._cuisine.core.file_copy("%s/jslib/old/images" % self.portal_dir,
                                     "%s/jslib/old/elfinder" % self.portal_dir, recursive=True)
        # link for ays
        self._cuisine.core.file_link(source='$codeDir/github/jumpscale/jumpscale_portal8/apps/portalbase/AYS81',
                                     destination='$appDir/portals/main/base/AYS81')

    def addSpace(self, spacepath):
        spacename = j.sal.fs.getBaseName(spacepath)
        dest_dir = j.sal.fs.joinPaths(self._cuisine.core.dir_paths[
            'appDir'], 'portals', 'main', 'base', spacename)
        self._cuisine.core.file_link(spacepath, dest_dir)

    def addactor(self, actorpath):
        actorname = j.sal.fs.getBaseName(actorpath)
        dest_dir = j.sal.fs.joinPaths(self._cuisine.core.dir_paths[
            'appDir'], 'portals', 'main', 'base', actorname)
        self._cuisine.core.file_link(actorpath, dest_dir)

    def serviceconnect(self, hrd):
        dest_cfg = j.sal.fs.joinPaths(self._cuisine.core.dir_paths['varDir'],
                                      'cfg', "portals", "main", "config.hrd")
        self._cuisine.core.file_write(dest_cfg, str(hrd))

    def start(self, passwd=None):
        """
        Start the portal
        passwd : if not None, change the admin password to passwd after start
        """
        dest_dir = j.sal.fs.joinPaths(self._cuisine.core.dir_paths['varDir'], 'cfg', 'portals', 'main')
        self._cuisine.core.dir_ensure(dest_dir)

        if not self._config:
            self.configure()

        self.serviceconnect(self._config)
        cmd = "jspython portal_start.py"
        self._cuisine.processmanager.ensure('portal', cmd=cmd, path=j.sal.fs.joinPaths(self.portal_dir, 'main'))

        if passwd is not None:
            self.set_admin_password(passwd)

    def stop(self):
        self._cuisine.processmanager.stop('portal')

    def set_admin_password(self, passwd):
        # wait for the admin user to be created by portal
        timeout = 60
        start = time.time()
        resp = self._cuisine.core.run('jsuser list', showout=False)[1]
        while resp.find('admin') == -1 and start + timeout > time.time():
            try:
                time.sleep(2)
                resp = self._cuisine.core.run('jsuser list', showout=False)[1]
            except:
                continue

        if resp.find('admin') == -1:
            self._cuisine.core.run('jsuser add --data admin:%s:admin:admin@mail.com:cockpit' % passwd)
        else:
            self._cuisine.core.run('jsuser passwd -ul admin -up %s' % passwd)
