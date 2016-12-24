from JumpScale import j
import time


base = j.tools.cuisine._getBaseClass()


class CuisinePortal(base):

    def _init(self):
        self.portal_dir = j.sal.fs.joinPaths(self.cuisine.core.dir_paths["JSAPPSDIR"], "portals/")
        self.main_portal_dir = j.sal.fs.joinPaths(self.portal_dir, 'main')
        self.cuisine.core.dir_ensure(self.main_portal_dir)
        self.cfg_path = j.sal.fs.joinPaths(self.main_portal_dir, 'config.hrd')

    def configure(self, mongodbip="127.0.0.1", mongoport=27017, influxip="127.0.0.1",
                  influxport=8086, grafanaip="127.0.0.1", grafanaport=3000, production=True):

        # go from template dir which go the file above
        content = self.cuisine.core.file_read('$TEMPLATEDIR/cfg/portal/config.hrd')

        hrd = j.data.hrd.get(content=content, prefixWithName=False)

        # ITS ALREADY THE DEFAULT IN THE CONFIG DIR
        # hrd.set('param.cfg.appdir', j.sal.fs.joinPaths(self.portal_dir, 'portalbase'))

        hrd.set('param.mongoengine.connection', {'host': mongodbip, 'port': mongoport})
        hrd.set('param.cfg.influx', {'host': influxip, 'port': influxport})
        hrd.set('param.cfg.grafana', {'host': grafanaip, 'port': grafanaport})
        hrd.set('param.cfg.production', production)

        if "darwin" in self.cuisine.platformtype.osname:
            hrd.set('param.cfg.port', '8200')

        self.cuisine.core.file_write(self.configPath, str(hrd))

    @property
    def configPath(self):
        return j.sal.fs.joinPaths(self.cuisine.core.dir_paths['VARDIR'],
                                  'cfg', "portals", "main", "config.hrd")

    def install(self, start=True, branch='', reset=False):
        """
        grafanaip and port should be the external ip of the machine
        Portal install will only install the portal and libs. No spaces but the system ones will be add by default.
        To add spaces and actors, please use addSpace and addactor
        """
        self.cuisine.bash.fixlocale()
        if not reset and self.doneGet("install"):
            self.linkCode()
            if start:
                self.start()
            return

        # install the dependencies if required
        self.installDeps(reset=reset)

        # pull repo with required branch ; then link dirs and files in required places
        self.getcode(branch=branch)
        self.linkCode()

        if start:
            self.start()

        self.doneSet("install")

    def installDeps(self, reset=False):
        """
        make sure new env arguments are understood on platform
        """
        if not reset and self.doneGet("installdeps"):
            return
        self.cuisine.development.pip.ensure(reset=reset)

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

        if not "darwin" in self.cuisine.platformtype.osname:
            self.cuisine.package.ensure('build-essential')
            self.cuisine.package.ensure('libssl-dev')
            self.cuisine.package.ensure('libffi-dev')
            self.cuisine.package.ensure('python3-dev')

        self.cuisine.development.pip.multiInstall(deps)

        if "darwin" in self.cuisine.platformtype.osname:
            self.cuisine.core.run("brew install libtiff libjpeg webp little-cms2")
            self.cuisine.core.run("brew install snappy")
            self.cuisine.core.run('CPPFLAGS="-I/usr/local/include -L/usr/local/lib" pip3 install python-snappy')
        else:
            self.cuisine.package.multiInstall(['libjpeg-dev', 'libffi-dev', 'zlib1g-dev'])

        # snappy install
        if not "darwin" in self.cuisine.platformtype.osname:
            self.cuisine.package.ensure('libsnappy-dev')
            self.cuisine.package.ensure('libsnappy1v5')

        self.cuisine.development.pip.install('python-snappy')

        self.doneSet("installdeps")

    def getcode(self, branch=''):
        if branch == "":
            branch = "8.2.0_portal_cleanup"
        self.cuisine.development.git.pullRepo(
            "https://github.com/Jumpscale/jumpscale_portal8.git", branch=branch)

    def linkCode(self):

        destjslib = self.cuisine.core.dir_paths['JSLIBDIR']

        # _, destjslib, _ = self.cuisine.core.run("js --quiet 'self.log(j.do.getPythonLibSystem(jumpscale=True))'",
        #                                          showout=False)
        #
        # if "darwin" in self.cuisine.platformtype.osname:
        #     # Needs refining,In osx destjslib='load dirs\n/usr/local/lib/python3.5/site-packages/JumpScale/'
        #     destjslib = destjslib.split("\n")[1]

        if self.cuisine.core.file_exists(destjslib):
            self.cuisine.core.file_link("%s/github/jumpscale/jumpscale_portal8/lib/portal" % self.cuisine.core.dir_paths["CODEDIR"],
                                        "%s/portal" % destjslib, symbolic=True, mode=None, owner=None, group=None)

        self.cuisine.core.run("js --quiet 'j.application.reload()'", showout=False, die=False)

        if not self.portal_dir.endswith("/"):
            self.portal_dir += '/'
        self.cuisine.core.dir_ensure(self.portal_dir)

        CODE_DIR = self.cuisine.core.dir_paths["CODEDIR"]
        self.cuisine.core.file_link("%s/github/jumpscale/jumpscale_portal8/jslib" % CODE_DIR,
                                    '%s/jslib' % self.portal_dir)
        self.cuisine.core.dir_ensure(j.sal.fs.joinPaths(self.portal_dir, 'portalbase'))
        self.cuisine.core.file_link("%s/github/jumpscale/jumpscale_portal8/apps/portalbase/system" % CODE_DIR,
                                    '%s/portalbase/system' % self.portal_dir)
        self.cuisine.core.file_link("%s/github/jumpscale/jumpscale_portal8/apps/portalbase/wiki" % CODE_DIR,
                                    '%s/portalbase/wiki' % self.portal_dir)
        self.cuisine.core.file_link("%s/github/jumpscale/jumpscale_portal8/apps/portalbase/macros" %
                                    CODE_DIR, '%s/portalbase/macros' % self.portal_dir)
        self.cuisine.core.file_link("%s/github/jumpscale/jumpscale_portal8/apps/portalbase/templates" %
                                    CODE_DIR, '%s/portalbase/templates' % self.portal_dir)

        self.cuisine.core.dir_ensure(self.main_portal_dir)

        self.cuisine.core.dir_ensure('%s/base/home/.space' % self.main_portal_dir)
        self.cuisine.core.file_ensure('%s/base/home/home.md' % self.main_portal_dir)

        self.cuisine.core.dir_ensure('$TEMPLATEDIR/cfg/portal')
        self.cuisine.core.file_copy(j.sal.fs.joinPaths(CODE_DIR, 'github/jumpscale/jumpscale_portal8/apps/portalbase/config.hrd'),
                                    '$TEMPLATEDIR/cfg/portal/config.hrd')
        self.cuisine.core.dir_ensure("$JSCFGDIR/portals/main/")
        self.cuisine.core.file_copy(j.sal.fs.joinPaths(CODE_DIR, 'github/jumpscale/jumpscale_portal8/apps/portalbase/config.hrd'),
                                    "$JSCFGDIR/portals/main/config.hrd")
        # copy portal_start.py
        self.cuisine.core.file_copy(j.sal.fs.joinPaths(CODE_DIR, 'github/jumpscale/jumpscale_portal8/apps/portalbase/portal_start.py'),
                                    self.main_portal_dir)
        self.cuisine.core.file_copy("%s/jslib/old/images" % self.portal_dir,
                                    "%s/jslib/old/elfinder" % self.portal_dir, recursive=True)
        # link for ays
        self.cuisine.core.file_link(source='$CODEDIR/github/jumpscale/jumpscale_portal8/apps/portalbase/AYS81',
                                    destination='$JSAPPSDIR/portals/main/base/AYS81')

    def addSpace(self, spacepath):
        spacename = j.sal.fs.getBaseName(spacepath)
        dest_dir = j.sal.fs.joinPaths(self.cuisine.core.dir_paths[
            'JSAPPSDIR'], 'portals', 'main', 'base', spacename)
        self.cuisine.core.file_link(spacepath, dest_dir)

    def addActor(self, actorpath):
        actorname = j.sal.fs.getBaseName(actorpath)
        dest_dir = j.sal.fs.joinPaths(self.cuisine.core.dir_paths[
            'JSAPPSDIR'], 'portals', 'main', 'base', actorname)
        self.cuisine.core.file_link(actorpath, dest_dir)

    def start(self, reset=False, passwd=None):
        """
        Start the portal
        passwd : if not None, change the admin password to passwd after start
        """
        self.cuisine.apps.mongodb.start()
        if not reset and self.doneGet("start"):
            return
        cmd = "jspython portal_start.py"
        self.cuisine.processmanager.ensure('portal', cmd=cmd, path=j.sal.fs.joinPaths(self.portal_dir, 'main'))

        if passwd is not None:
            self.set_admin_password(passwd)

        self.doneSet("start")

    def stop(self):
        self.cuisine.processmanager.stop('portal')

    def set_admin_password(self, passwd):
        # wait for the admin user to be created by portal
        timeout = 60
        start = time.time()
        resp = self.cuisine.core.run('jsuser list', showout=False)[1]
        while resp.find('admin') == -1 and start + timeout > time.time():
            try:
                time.sleep(2)
                resp = self.cuisine.core.run('jsuser list', showout=False)[1]
            except:
                continue

        if resp.find('admin') == -1:
            self.cuisine.core.run('jsuser add --data admin:%s:admin:admin@mail.com:cockpit' % passwd)
        else:
            self.cuisine.core.run('jsuser passwd -ul admin -up %s' % passwd)
