
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


    @actionrun(action=True)
    def agentcontroller(self, start=True):
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
            dest = self.cuisine.golang.get(url)

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
            dest = self.cuisine.golang.get(url)

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
