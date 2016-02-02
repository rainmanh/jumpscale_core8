
from JumpScale import j
from CuisinePortal import CuisinePortal


from ActionDecorator import ActionDecorator
class actionrun(ActionDecorator):
    def __init__(self,*args,**kwargs):
        ActionDecorator.__init__(self,*args,**kwargs)
        self.selfobjCode="cuisine=j.tools.cuisine.getFromId('$id');selfobj=cuisine.installerdevelop"


class CuisineInstallerDevelop():

    def __init__(self,executor,cuisine):
        self.executor=executor
        self.cuisine=cuisine
        self._portal = None

    @property
    def portal(self):
        if self._portal is None:
            self._portal = CuisinePortal(self.executor, self.cuisine)
        return self._portal

    @actionrun(action=True)

    def python(self):
        C="""
        libpython3.5-dev
        python3.5-dev
        libffi-dev
        gcc
        build-essential
        autoconf
        libtool
        pkg-config
        libpq-dev
        libsqlite3-dev
        #net-tools
        """
        self.cuisine.package.multiInstall(C)

    @actionrun(action=True)
    def pip(self):
        self.cuisine.installer.base()
        self.python()
        cmd="""
            cd /tmp
            rm -rf get-pip.py
            wget https://bootstrap.pypa.io/get-pip.py
        """
        self.cuisine.run_script(cmd)
        self.cuisine.run("cd /tmp;python3.5 get-pip.py")


    @actionrun(action=True)
    def jumpscale(self):

        self.pip(action=True)

        C = """
        set +ex
        pskill redis-server #will now kill too many redis'es, should only kill the one not in docker
        pskill redis #will now kill too many redis'es, should only kill the one not in docker
        umount -fl /optrw
        # apt-get remove redis-server -y
        rm -rf /overlay/js_upper
        rm -rf /overlay/js_work
        rm -rf /optrw
        js8 stop
        pskill js8
        umount -f /opt
        apt-get install tmux fuse -y
        """
        self.cuisine.run_script(C,action=True)

        #install brotli
        C="""
        cd /tmp
        sudo rm -rf brotli/
        git clone https://github.com/google/brotli.git
        cd /tmp/brotli/
        python setup.py install
        cd tests
        make
        cd ..
        cp /tmp/brotli/tools/bro /usr/local/bin/
        rm -rf /tmp/brotli
        """
        self.cuisine.run_script(C,action=True)

        #python etcd
        C="""
        cd /tmp
        git clone https://github.com/jplana/python-etcd.git
        cd python-etcd
        python3.5 setup.py install
        """
        self.cuisine.run_script(C,action=True)


        C="""
        paramiko

        msgpack-python
        redis
        credis
        aioredis


        mongoengine

        bcrypt
        blosc
        certifi
        docker-py

        gitlab3
        gitpython
        html2text

        # pysqlite
        click
        influxdb
        ipdb
        ipython --upgrade
        jinja2
        netaddr

        reparted
        pytoml
        pystache
        pymongo
        psycopg2
        pathtools
        psutil

        pytz
        requests
        sqlalchemy
        urllib3
        zmq
        pyyaml
        websocket
        marisa-trie
        pylzma
        ujson
        watchdog
        """
        self.cuisine.pip.multiInstall(C,action=True,upgrade=True)

        #gevent
        C="""
        pip3 install 'cython>=0.23.4' git+git://github.com/gevent/gevent.git#egg=gevent
        """
        self.cuisine.run_script(C,action=True)

    @actionrun(action=True)
    def jumpscale8(self):

        self.cuisine.installer.pip()
        self.cuisine.pip.upgrade("pip")
        libDeps = ["'cython>=0.23.4' git+git://github.com/gevent/gevent.git#egg=gevent", "paramiko", "msgpack-python", "redis", "credis", "aioredis", "mongoengine", "bcrypt",
         "blosc", "certifi", "docker-py", "gitlab3", "gitpython", "html2text","click", "influxdb", "ipdb", "ipython", "jinja2",
         "netaddr", "reparted", "pytoml", "pystache", "pymongo", "psycopg2", "pathtools", "psutil", "pytz", "requests", "sqlalchemy",
          "urllib3", "zmq", "pyyaml", "websocket", "marisa-trie", "pylzma", "ujson", "watchdog"]
        for dep in libDeps:
            self.cuisine.pip.install(dep)

        if self.cuisine.isUbuntu:
            self.cuisine.run('cd /tmp;rm -f install.sh;curl -k https://raw.githubusercontent.com/Jumpscale/jumpscale_core8/master/install/install.sh > install.sh;bash install.sh')
        elif self.cuisine.isMac:
            cmd = """sudo mkdir -p /opt
            sudo chown -R despiegk:root /opt
            ruby -e \"$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/master/install)\""""
            self.cuisine.run(cmd)
        else:
            raise RuntimeError("platform not supported yet")


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
