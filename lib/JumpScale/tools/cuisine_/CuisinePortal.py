from JumpScale import j

from ActionDecorator import ActionDecorator
class actionrun(ActionDecorator):
    def __init__(self,*args,**kwargs):
        ActionDecorator.__init__(self,*args,**kwargs)
        self.selfobjCode="cuisine=j.tools.cuisine.getFromId('$id');selfobj=cuisine.installerdevelop.portal"


class CuisinePortal(object):

    def __init__(self,executor,cuisine):
        self.executor=executor
        self.cuisine=cuisine

    def install(self, minimal=False, start=True, mongodbip="127.0.0.1", mongoport=27017, login="", passwd=""):
        if not self.cuisine.isMac:
            self.cuisine.installerdevelop.jumpscale8()
            self.cuisine.pip.upgrade("pip")
        self.installDeps()
        self.getcode()
        self.linkCode(minimal=minimal)
        self.mongoconnect(ip=mongodbip, port=mongoport)
        self.changeEve()
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
        gevent==1.1rc2
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
        # watchdog
        websocket
        websocket-client
        Werkzeug
        wheel
        # zmq
        """

        # def installPip(name):
        #     self.cuisine.installer.pip()

        actionout = None
        for dep in deps.split("\n"):
            dep = dep.strip()
            if dep.strip() == "":
                continue
            if dep.strip()[0] == "#":
                continue
            dep = dep.split("=", 1)[0]
            self.cuisine.pip.install(dep)


    @actionrun(action=True)
    def getcode(self):
        j.do.pullGitRepo("git@github.com:Jumpscale/jumpscale_portal8.git", executor=self.executor)

    @actionrun(action=True)
    def linkCode(self, minimal=False):
        destjslib = j.do.getPythonLibSystem(jumpscale=True)
        self.cuisine.file_link("%s/github/jumpscale/jumpscale_portal8/lib/portal" % j.dirs.codeDir, "%s/portal" % destjslib, symbolic=True, mode=None, owner=None, group=None)
        self.cuisine.file_link("%s/github/jumpscale/jumpscale_portal8/lib/portal" % j.dirs.codeDir, "%s/portal" % j.dirs.jsLibDir)

        self.cuisine.run("js 'j.application.reload()'")

        portaldir = j.sal.fs.joinPaths(j.dirs.base, "apps", "portals")
        if not portaldir.endswith("/"):
            portaldir +='/'
        self.cuisine.dir_ensure(portaldir)
        self.cuisine.file_link("%s/github/jumpscale/jumpscale_portal8/jslib" % j.dirs.codeDir, '%s/jslib' % portaldir)
        self.cuisine.dir_ensure(j.sal.fs.joinPaths(portaldir, 'portalbase'))
        self.cuisine.file_link("%s/github/jumpscale/jumpscale_portal8/apps/portalbase/system" %
                         j.dirs.codeDir,  '%s/portalbase/system' % portaldir)
        self.cuisine.file_link("%s/github/jumpscale/jumpscale_portal8/apps/portalbase/wiki" %
                         j.dirs.codeDir, '%s/portalbase/wiki' % portaldir)
        self.cuisine.file_link("%s/github/jumpscale/jumpscale_portal8/apps/portalbase/macros" %
                         j.dirs.codeDir, '%s/portalbase/macros' % portaldir)
        self.cuisine.file_link("%s/github/jumpscale/jumpscale_portal8/apps/portalbase/templates" %
                         j.dirs.codeDir, '%s/portalbase/templates' % portaldir)

        exampleportaldir = '%sexample/base' % portaldir
        self.cuisine.dir_ensure(exampleportaldir)

        if not minimal:
            for space in self.cuisine.fs_find("%s/github/jumpscale/jumpscale_portal8/apps/gridportal/base" % j.dirs.codeDir,recursive=False):
                spacename = j.sal.fs.getBaseName(space)
                if not spacename == 'home':
                    self.cuisine.dir_ensure(j.sal.fs.joinPaths(exampleportaldir, 'gridportal'))
                    self.cuisine.file_link(space, j.sal.fs.joinPaths(exampleportaldir, 'gridportal', spacename))
            self.cuisine.dir_ensure('%s/home/.space' %exampleportaldir)
            self.cuisine.file_ensure('%s/home/home.md' %exampleportaldir)

        dest = exampleportaldir = '%sexample' % portaldir
        self.cuisine.dir_ensure(dest)
        self.cuisine.file_copy(j.sal.fs.joinPaths(j.dirs.codeDir, 'github/jumpscale/jumpscale_portal8/apps/portalbase/portal_start.py'), exampleportaldir)
        self.cuisine.file_copy(j.sal.fs.joinPaths(j.dirs.codeDir, 'github/jumpscale/jumpscale_portal8/apps/portalbase/config.hrd'), exampleportaldir)
        self.cuisine.file_copy(j.sal.fs.joinPaths(j.dirs.codeDir, 'github/jumpscale/jumpscale_portal8/apps/portalbase/portal_start.py'), exampleportaldir)
        self.cuisine.file_copy(j.sal.fs.joinPaths(j.dirs.codeDir, 'github/jumpscale/jumpscale_portal8/apps/portalbase/config.hrd'), exampleportaldir)
        # j.dirs.replaceFilesDirVars("%s/example/config.hrd" % portaldir)
        self.cuisine.file_copy("%s/jslib/old/images" % portaldir, "%s/jslib/old/elfinder" % portaldir, recursive=True)

    @actionrun(action=True)
    def mongoconnect(self, ip, port):
        cfg_path = j.sal.fs.joinPaths(j.dirs.base, 'apps/portals/example/config.hrd')
        content = self.cuisine.file_read(cfg_path)
        tmp = j.sal.fs.getTempFileName()
        hrd = j.data.hrd.get(content=content, path=tmp)
        hrd.set('param.mongoengine.connection', {'host': ip, 'port': port})
        hrd.save()
        self.cuisine.file_upload_local(tmp, cfg_path)

    @actionrun(action=True)
    def changeEve(self):
        path = j.sal.fs.joinPaths(j.do.getPythonLibSystem(jumpscale=False), "eve_docs", "config.py")
        self.cuisine.run("2to3 -f all -w %s" % path)

    @actionrun(action=True)
    def start(self):
        portaldir = j.sal.fs.joinPaths(j.dirs.base,'apps/portals/')
        exampleportaldir = j.sal.fs.joinPaths(portaldir,'example/')
        cmd = "cd %s; jspython portal_start.py" % exampleportaldir
        self.cuisine.tmux.createSession("portal", ['portal'])
        self.cuisine.tmux.executeInScreen('portal', 'portal', cmd=cmd)
    #
    # if start:
    #     j.actions.add(startmethod)
    # else:
    #     print('To run your portal, navigate to %s/apps/portals/example/ and run "jspython portal_start.py"' % j.dirs.base)
    # startmethod()
    # j.actions.run()


        #cd /usr/local/Cellar/mongodb/3.2.1/bin/;./mongod --dbpath /Users/kristofdespiegeleer1/optvar/mongodb


        #@todo install gridportal as well
        #@link example spaces
        #@eve issue
        #@explorer issue
