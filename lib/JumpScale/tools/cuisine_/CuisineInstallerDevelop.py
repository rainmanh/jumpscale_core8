
from JumpScale import j
# import os

# import socket

from ActionDecorator import ActionDecorator
class actionrun(ActionDecorator):
    def __init__(self,*args,**kwargs):
        ActionDecorator.__init__(self,*args,**kwargs)
        self.selfobjCode="cuisine=j.tools.cuisine.getFromId('$id');selfobj=cuisine.installerdevel"



class CuisineInstallerDevelop():

    def __init__(self,executor,cuisine):
        self.executor=executor
        self.cuisine=cuisine

    @actionrun(action=True)
    def golang():
        rc, out = self.cuisine.run("which go", die=False)
        if rc > 0:
            if sys.platform.startswith("OSX"):
                self.cuisine.run("brew install golang")
            else:
                self.cuisine.run("apt-get install golang -y --force-yes")

        from IPython import embed
        print ("DEBUG NOW oioioi")
        embed()
        
        os.environ.setdefault("GOROOT", '/usr/lib/go/')
        os.environ.setdefault("GOPATH", '/opt/go')
        j.sal.fs.createDir(os.environ['GOPATH'])
        print ('GOPATH:', os.environ["GOPATH"])
        print ('GOROOT:', os.environ["GOROOT"])
        j.sal.fs.touch(j.sal.fs.joinPaths(os.environ["HOME"], '.bash_profile'), overwrite=False)
        path = os.environ.get('PATH')
        os.environ['PATH'] = '%s:%s/bin' % (path, os.environ['GOPATH'])
        self.executor.execute('go get github.com/tools/godep')
        self.executor.execute('go get github.com/rcrowley/go-metrics')


    def installAgentcontroller(self, start=True):
        """
        config: https://github.com/Jumpscale/agent2/wiki/agent-configuration
        """
        j.actions.setRunId("installAgentController")

        agentAppDir = j.sal.fs.joinPaths(j.dirs.base, "apps", "agent8")
        agentcontrollerAppDir = j.sal.fs.joinPaths(j.dirs.base, "apps", "agentcontroller8")
        syncthingAppDir = j.sal.fs.joinPaths(j.dirs.base, "apps", "syncthing")
        os.environ.setdefault("GOROOT", '/usr/lib/go/')
        os.environ.setdefault("GOPATH", '/opt/go')

        def upgradePip():
            self.executor.execute("pip3 install --upgrade pip")

        def pythonLibInstall():
            self.executor.execute("pip3 install pytoml")



        def syncthing_build(appbase):
            url = "git@github.com:syncthing/syncthing.git"
            dest = j.do.pullGitRepo(url, dest='%s/src/github.com/syncthing/syncthing' % os.environ['GOPATH'])
            self.executor.execute('cd %s && godep restore' % dest)
            self.executor.execute("cd %s && ./build.sh noupgrade" % dest)
            tarfile = j.sal.fs.find(dest, 'syncthing*.tar.gz')[0]
            tar = j.tools.tarfile.get(j.sal.fs.joinPaths(dest, tarfile))
            tar.extract(dest)
            path = tarfile.rstrip('.tar.gz')
            j.sal.fs.copyFile(j.sal.fs.joinPaths(dest, path, 'syncthing'), '%s/bin/' % os.environ['GOPATH'])
            j.sal.fs.copyFile(j.do.joinPaths(os.environ['GOPATH'], 'bin', 'syncthing'), j.sal.fs.joinPaths(appbase, "syncthing"))

        def agent_build(appbase):
            url = "git@github.com:Jumpscale/agent2.git"
            dest = j.tools.golang.build(url)

            j.sal.fs.copyFile(j.sal.fs.joinPaths(os.environ['GOPATH'], 'bin', "agent2"), j.sal.fs.joinPaths(appbase, "agent2"))
            j.sal.fs.copyFile(j.sal.fs.joinPaths(os.environ['GOPATH'], 'bin', "syncthing"), j.sal.fs.joinPaths(appbase, "syncthing"))

            j.do.createDir(appbase)

            # link extensions
            extdir = j.sal.fs.joinPaths(appbase, "extensions")
            j.do.delete(extdir)
            j.do.symlink("%s/extensions" % dest, extdir)

            # manipulate config file
            cfgfile = '%s/agent.toml' % appbase
            j.do.copyFile("%s/agent.toml" % dest, cfgfile)

            j.sal.fs.copyDirTree("%s/conf" % dest, j.sal.fs.joinPaths(appbase, "conf"))

            #cfg = j.data.serializer.toml.load(cfgfile)

            #j.data.serializer.toml.dump(cfgfile, cfg)

        def agentcontroller_build(appbase):
            url = "git@github.com:Jumpscale/agentcontroller2.git"
            dest = j.tools.golang.build(url)

            destfile = j.sal.fs.joinPaths(appbase, "agentcontroller2")
            j.sal.fs.copyFile(j.do.joinPaths(os.environ['GOPATH'], 'bin', "agentcontroller2"), destfile)

            j.do.createDir(appbase)
            cfgfile = '%s/agentcontroller.toml' % appbase
            j.do.copyFile("%s/agentcontroller.toml" % dest, cfgfile)

            extdir = j.sal.fs.joinPaths(appbase, "extensions")
            j.do.delete(extdir)
            j.sal.fs.createDir(extdir)
            j.do.symlinkFilesInDir("%s/extensions" % dest, extdir, delete=True, includeDirs=False)

            cfg = j.data.serializer.toml.load(cfgfile)

            cfg['jumpscripts']['python_path'] = "%s:%s" % (extdir, j.dirs.jsLibDir)

            j.data.serializer.toml.dump(cfgfile, cfg)

        j.actions.add(upgradePip)
        j.actions.add(pythonLibInstall)
        j.actions.add(prepare_go)
        j.actions.add(syncthing_build, args={'appbase': syncthingAppDir})
        j.actions.add(agent_build, args={"appbase": agentAppDir})
        j.actions.add(agentcontroller_build, args={"appbase": agentcontrollerAppDir})
        j.actions.run()

        def startAgent(appbase):

            cfgfile_agent = j.do.joinPaths(appbase, "agent2.toml")
            j.sal.nettools.waitConnectionTest("127.0.0.1", 8966, timeout=2)
            print("connection test ok to agentcontroller")
            j.sal.tmux.executeInScreen("main", screenname="agent", cmd="./agent2 -c %s" % cfgfile_agent, wait=0, cwd=appbase, env=None, user='root', tmuxuser=None)

        def startAgentController(appbase):
            cfgfile_ac = j.do.joinPaths(appbase, "agentcontroller2.toml")
            j.sal.tmux.executeInScreen("main", screenname="ac", cmd="./agentcontroller2 -c %s" % cfgfile_ac, wait=0, cwd=appbase, env=None, user='root', tmuxuser=None)

        if start:
            j.actions.add(startAgent, args={"appbase": agentAppDir})
            j.actions.add(startAgentController, args={"appbase": agentcontrollerAppDir})
            j.actions.run()
        else:
            print('To run your agent, navigate to "%s" adn to "%s" and do "./agent2 -c agent2.toml"' % agentAppDir)
            print('To run your agentcontroller, navigate to "%s" adn to "%s" and do "./agentcontroller2 -c agentcontroller2.toml"' % agentcontrollerAppDir)

    def installPortal(self, minimal=False, start=True, mongodbip="127.0.0.1", mongoport=27017, login="", passwd=""):

        j.actions.setRunId("installportal")

        def upgradePip():
            j.do.execute("pip3 install --upgrade pip")
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
                j.do.execute("pip3 install --upgrade %s " % name)

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
            j.do.pullGitRepo("git@github.com:Jumpscale/jumpscale_portal8.git")
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

            self.cuisine.file_upload("%s/github/jumpscale/jumpscale_portal8/apps/portalbase/portal_start.py" % j.dirs.codeDir, '%sexample' % portaldir)
            self.cuisine.file_upload("%s/github/jumpscale/jumpscale_portal8/apps/portalbase/config.hrd" % j.dirs.codeDir, '%sexample' % portaldir)
            j.dirs.replaceFilesDirVars("%s/example/config.hrd" % portaldir)
            j.sal.fs.copyDirTree("%s/jslib/old/images" % portaldir, "%s/jslib/old/elfinder" % portaldir)

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
            self.executor.execute("2to3 -f all -w %s" % evedocs[0])

        j.actions.add(changeEve, deps=[actionGetcode, actioninstall])

        def startmethod():
            portaldir = '%s/apps/portals/' % j.do.BASE
            exampleportaldir = '%sexample/' % portaldir
            cmd = "cd %s; jspython portal_start.py" % exampleportaldir
            j.sal.tmux.executeInScreen("portal", "portal", cmd, wait=0, cwd=None, env=None, user='root', tmuxuser=None)

            # j.do.execute()
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
