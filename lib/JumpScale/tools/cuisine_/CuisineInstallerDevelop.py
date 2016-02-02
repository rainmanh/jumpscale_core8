
from JumpScale import j
#do those apply to remote exec 
# import os

# import socket

from ActionDecorator import ActionDecorator
class actionrun(ActionDecorator):
    def __init__(self,*args,**kwargs):
        ActionDecorator.__init__(self,*args,**kwargs)
        self.selfobjCode="cuisine=j.tools.cuisine.getFromId('$id');selfobj=cuisine.installerdevelop"



class CuisineInstallerDevelop():

    def __init__(self,executor,cuisine):
        self.executor=executor
        self.cuisine=cuisine

    def _linkfilesindir(self, dir_path, dest):
        for fil in self.cuisine.fs_find(dir_path):
            dest_fil = "%s/%s" %(dest, dir_path.split("/")[-1:][0])
            self.cuisine.dir_remove(dest_fil, recursive=False)
            self.cuisine.file_link(fil, dest_fil)
    def _joinpath(self, *args):
        path = ""
        for arg in args:
            path += "/%s"%arg
        return path
    def _copyfile(self, dir_path, dest, overwriteTarget=True,  recursive=False):
        recurse = "r" if recursive else ""
        overwrite = "f" if overwriteTarget else ""
        self.cuisine.run("cp -%s%s %s %s" %(recurse, overwrite, dir_path, dest))
        

    @actionrun(action=True)
    def golang(self):
        rc, out = self.cuisine.run("which go", die=False)
        if rc > 0:
            if self.cuisine.isMac:
                self.cuisine.run("brew install golang")
            else:
                self.cuisine.run("apt-get install golang -y --force-yes")

       
        self.executor.env["GOROOT"]=self.executor.env.get('GOROOT','/usr/lib/go/')
        self.executor.env["GOPATH"]=self.executor.env.get('GOPATH','/opt/go/')
        self.cuisine.dir_ensure(self.executor.env['GOPATH'])
        print ('GOPATH:', self.executor.env["GOPATH"])
        print ('GOROOT:', self.executor.env["GOROOT"])
        self.cuisine.file_ensure(self._joinpath(self.cuisine.run("echo $HOME"), '.bash_profile'))
        path = self.cuisine.run("echo $PATH")
        self.executor.env['PATH'] = '%s:%s/bin' % (path, self.executor.env['GOPATH'])
        self.cuisine.run('go get github.com/tools/godep')
        self.cuisine.run('go get github.com/rcrowley/go-metrics')

    @actionrun(action=True)
    def installAgentcontroller(self, start=True):
        """
        config: https://github.com/Jumpscale/agent2/wiki/agent-configuration
        """
        j.actions.setRunId("installAgentController")

        agentAppDir = self._joinpath(j.dirs.base, "apps", "agent8")
        agentcontrollerAppDir = self._joinpath(j.dirs.base, "apps", "agentcontroller8")
        syncthingAppDir = self._joinpath(j.dirs.base, "apps", "syncthing")
        self.executor.env["GOROOT"] = self.executor.env.get("GOROOT", '/usr/lib/go/')
        self.executor.env["GOPATH"] = self.executor.env.get("GOPATH", '/opt/go')

        def upgradePip():
            self.cuisine.run("pip3 install --upgrade pip")

        def pythonLibInstall():
            self.cuisine.run("pip3 install pytoml")



        def syncthing_build(appbase):
            url = "git@github.com:syncthing/syncthing.git"
            dest = self.cuisine.git.pullRepo(url, dest='%s/src/github.com/syncthing/syncthing' % self.executor.env['GOPATH'])
            self.cuisine.run('cd %s && godep restore' % dest)
            self.cuisine.run("cd %s && ./build.sh noupgrade" % dest)
            self.cuisine.dir_ensure(appbase, recursive=True)
            self._copyfile(self._joinpath(dest, 'syncthing'), '%s/bin/' % self.executor.env['GOPATH'])
            self._copyfile(self._joinpath(self.executor.env['GOPATH'], 'bin', 'syncthing'), appbase)

        def agent_build(appbase):
            url = "git@github.com:Jumpscale/agent2.git"
            dest = j.tools.golang.build(url)

            self._copyfile(self._joinpath(self.executor.env['GOPATH'], 'bin', "agent2"), self._joinpath(appbase, "agent2"))
            self._copyfile(self._joinpath(self.executor.env['GOPATH'], 'bin', "syncthing"), self._joinpath(appbase, "syncthing"))

            self.cuisine.dir_ensure(appbase, recursive=True)

            # link extensions
            extdir = self._joinpath(appbase, "extensions")
            self.cuisine.dir_remove(extdir)
            self.cuisine.file_link("%s/extensions" % dest, extdir)

            # manipulate config file
            cfgfile = '%s/agent.toml' % appbase
            self._copyfile("%s/agent.toml" % dest, cfgfile)

            self._copyfile("%s/conf" % dest, self._joinpath(appbase, "conf"), recursive=True )

            #cfg = j.data.serializer.toml.load(cfgfile)

            #j.data.serializer.toml.dump(cfgfile, cfg)

        def agentcontroller_build(appbase):
            url = "git@github.com:Jumpscale/agentcontroller2.git"
            dest = j.tools.golang.build(url)

            destfile = self._joinpath(appbase, "agentcontroller2")
            self._copyfile(self._joinpath(self.executor.env['GOPATH'], 'bin', "agentcontroller2"), destfile)

            self.cuisine.dir_ensure(appbase, recursive=True)
            cfgfile = '%s/agentcontroller.toml' % appbase
            self._copyfile("%s/agentcontroller.toml" % dest, cfgfile)

            extdir = self._joinpath(appbase, "extensions")
            self.cuisine.dir_remove(extdir)
            self.cuisine.dir_ensure(extdir)
            self._linkfilesindir("%s/extensions" % dest, extdir)

            cfg = j.data.serializer.toml.load(cfgfile)

            cfg['jumpscripts']['python_path'] = "%s:%s" % (extdir, j.dirs.jsLibDir)

            j.data.serializer.toml.dump(cfgfile, cfg)

        upgradePip()
        pythonLibInstall()
        self.golang()
        syncthing_build(appbase=syncthingAppDir)
        agent_build(appbase=agentAppDir)
        agentcontroller_build(appbase=agentcontrollerAppDir)

        def startAgent(appbase):

            cfgfile_agent = self._joinpath(appbase + "agent2.toml")
            j.sal.nettools.waitConnectionTest("127.0.0.1", 8966, timeout=2)
            print("connection test ok to agentcontroller")
            self.cuisine.tmux.executeInScreen("main", screenname="agent", cmd="./agent2 -c %s" % cfgfile_agent, wait=0, cwd=appbase, env=None, user='root', tmuxuser=None)

        def startAgentController(appbase):
            cfgfile_ac = self._joinpath(appbase, "agentcontroller2.toml")
            self.cuisine.tmux.executeInScreen("main", screenname="ac", cmd="./agentcontroller2 -c %s" % cfgfile_ac, wait=0, cwd=appbase, env=None, user='root', tmuxuser=None)

        if start:
            startAgent(appbase = agentAppDir)
            startAgentController(appbase = agentcontrollerAppDir)
          # j.actions.run()
        else:
            print('To run your agent, navigate to "%s" adn to "%s" and do "./agent2 -c agent2.toml"' % agentAppDir)
            print('To run your agentcontroller, navigate to "%s" adn to "%s" and do "./agentcontroller2 -c agentcontroller2.toml"' % agentcontrollerAppDir)

    def installPortal(self, minimal=False, start=True, mongodbip="127.0.0.1", mongoport=27017, login="", passwd=""):

        j.actions.setRunId("installportal")

        def upgradePip():
            self.cuisine.run("pip3 install --upgrade pip")
        actionUpgradePIP = j.actions.add(upgradePip)

        def installDeps(actionin):
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

            def installPip(name):
                self.cuisine.run("pip3 install --upgrade %s " % name)

            actionout = None
            for dep in deps.split("\n"):
                dep = dep.strip()
                if dep.strip() == "":
                    continue
                if dep.strip()[0] == "#":
                    continue
                dep = dep.split("=", 1)[0]
                actionout = j.actions.add(
                    installPip, args={"name": dep}, retry=2, deps=[actionin, actionout])

            return actionout
        actiondeps = installDeps(actionUpgradePIP)

        def getcode():
            self.cuisine.git.pullRepo("git@github.com:Jumpscale/jumpscale_portal8.git")
        actionGetcode = j.actions.add(getcode, deps=[])

        def install():
            destjslib = j.do.getPythonLibSystem(jumpscale=True)
            self.cuisine.file_link("%s/github/jumpscale/jumpscale_portal8/lib/portal" % j.dirs.codeDir, "%s/portal" % destjslib, symbolic=True, mode=None, owner=None, group=None)
            self.cuisine.file_link("%s/github/jumpscale/jumpscale_portal8/lib/portal" % j.dirs.codeDir, "%s/portal" % j.dirs.jsLibDir)

            j.application.reload()

            portaldir = '%s/apps/portals/' % j.dirs.base
            self.cuisine.dir_ensure(portaldir)
            self.cuisine.file_link("%s/github/jumpscale/jumpscale_portal8/jslib" % j.dirs.codeDir, '%s/jslib' % portaldir)
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
                       self.cuisine.file_link(space, '%s/gridportal/%s' %(exampleportaldir,spacename))
                self.cuisine.dir_ensure('%s/home/.space' %exampleportaldir)
                self.cuisine.file_ensure('%s/home/home.md' %exampleportaldir)

            self._copyfile("%s/github/jumpscale/jumpscale_portal8/apps/portalbase/portal_start.py" % j.dirs.codeDir, '%sexample' % portaldir)
            self._copyfile("%s/github/jumpscale/jumpscale_portal8/apps/portalbase/config.hrd" % j.dirs.codeDir, '%sexample' % portaldir)
            j.dirs.replaceFilesDirVars("%s/example/config.hrd" % portaldir)
            self._copyfile("%s/jslib/old/images" % portaldir, "%s/jslib/old/elfinder" % portaldir, recursive=True)

        actioninstall = j.actions.add(install, deps=[actiondeps])

        def mongoconnect():
            cfg = j.data.hrd.get('%s/apps/portals/example/config.hrd'%j.dirs.base)
            cfg.set('param.mongoengine.connection', {'host':mongodbip, 'port':mongoport})
            cfg.save()

        j.actions.add(mongoconnect, deps=[actioninstall], args={})

        def changeEve():
            self.executor = j.tools.self.executor.getLocal()
            evedocs = j.sal.fs.walk(j.do.getPythonLibSystem(jumpscale=False), recurse=0, pattern='eve_docs', return_folders=1, return_files=0)
            if not evedocs:
                return
            self.cuisine.run("2to3 -f all -w %s" % evedocs[0])

        j.actions.add(changeEve, deps=[actionGetcode, actioninstall])

        def startmethod():
            portaldir = '%s/apps/portals/' % j.do.BASE
            exampleportaldir = '%sexample/' % portaldir
            cmd = "cd %s; jspython portal_start.py" % exampleportaldir
            self.cuisine.tmux.executeInScreen("portal", "portal", cmd, wait=0, cwd=None, env=None, user='root', tmuxuser=None)

            # self.cuisine.run()
        if start:
            j.actions.add(startmethod)
        else:
            print('To run your portal, navigate to %s/apps/portals/example/ and run "jspython portal_start.py"' % j.dirs.base)

        j.actions.run()


        #cd /usr/local/Cellar/mongodb/3.2.1/bin/;./mongod --dbpath /Users/kristofdespiegeleer1/optvar/mongodb


        #@todo install gridportal as well
        #@link example spaces
        #@eve issue
        #@explorer issue

    #@todo installer for trueid env
    #@todo installer for g8exchange
    @actionrun(action=True)
    def aydostore(self, addr='0.0.0.0:8090', backend="/tmp/aydostor"):
        """
        Install aydostore
        @input addr, address and port on which the service need to listen. e.g. : 0.0.0.0:8090
        @input backend, directory where to save the data push to the store
        """
        def install():
            script = """
            set -ex
            rm -f /usr/bin/aydostorx
            wget https://stor.jumpscale.org/storx/static/aydostorex -O /usr/bin/aydostorx
            chmod +x /usr/bin/aydostorx
            """
            self.cuisine.run_script(script)

        def configure():
            self.cuisine.dir_ensure("/etc/aydostorx")
            config = {
                'listen_addr': addr,
                'store_root': backend,
            }
            j.data.serializer.toml.dump("/etc/aydostorx/config.toml", config)

        def start():
            cmd = '/usr/bin/aydostorx -c /etc/aydostorx/config.toml'
            self.cuisine.tmux.createSession('aydostorx', ['aydostorx'])
            self.cuisine.tmux.executeInScreen('aydostorx', 'aydostorx', cmd)
        install()
        configure()
        start()
