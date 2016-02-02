
from JumpScale import j
from CuisinePortal import CuisinePortal


from ActionDecorator import ActionDecorator
class actionrun(ActionDecorator):
    def __init__(self,*args,**kwargs):
        ActionDecorator.__init__(self,*args,**kwargs)
        self.selfobjCode="cuisine=j.tools.cuisine.getFromId('$id');selfobj=cuisine.installerdevel"


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
