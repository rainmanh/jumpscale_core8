from JumpScale import j

# TODO: needs to be checked how this needs to be used, maybe no longer relevant in line to the building we do now

app = j.tools.cuisine._getBaseAppClass()


class CuisineG8OSCore(app):

    def __init__(self, executor, cuisine):
        self._executor = executor
        self._cuisine = cuisine

    def build(self, start=True, gid=None, nid=None, install=True):
        """
        builds and setsup dependencies of agent to run , given gid and nid
        neither can be the int zero, can be ommited if start=False
        """
        # deps
        self._cuisine.development.js8.installDeps()
        self._cuisine.apps.redis.install(reset=True)
        self._cuisine.apps.redis.start()
        self._cuisine.apps.mongodb.build(start=False)

        self._cuisine.apps.syncthing.build(start=False)

        self._cuisine.tmux.killWindow("main", "core")

        self._cuisine.process.kill("core")

        self._cuisine.core.dir_ensure("$tmplsDir/cfg/core", recursive=True)
        self._cuisine.core.file_ensure("$tmplsDir/cfg/core/.mid")

        url = "github.com/g8os/core"
        self._cuisine.development.golang.godep(url)


        self._cuisine.core.run("cd $goDir/src/github.com/g8os/core && go build .", profile=True)

        if install:
            self.install(start, gid, nid)


    def install(self, start=True, gid=None, nid=None):
        """
        download, install, move files to appropriate places, and create relavent configs
        """
        sourcepath = "$goDir/src/github.com/g8os/core"
        self._cuisine.core.file_move("%s/core" % sourcepath, "$binDir/core")

        # copy extensions
        self._cuisine.core.dir_remove("$tmplsDir/cfg/core/extensions")
        self._cuisine.core.file_copy("%s/extensions" % sourcepath, "$tmplsDir/cfg/core", recursive=True)
        self._cuisine.core.file_copy("%s/g8os.toml" % sourcepath, "$tmplsDir/cfg/core")
        self._cuisine.core.dir_ensure("$tmplsDir/cfg/core/conf/")
        self._cuisine.core.file_copy("{0}basic.jumpscripts.toml {0}basic.syncthing.toml".format(sourcepath+"/conf/"), "$tmplsDir/cfg/core/conf/", recursive=True)
        if self._cuisine.core.isArch:
            self._cuisine.core.file_copy("{0}sshd-arch.toml".format(sourcepath+"/conf.extra/"), "$tmplsDir/cfg/core/conf/", recursive=True)
        if self._cuisine.core.isUbuntu:
            self._cuisine.core.file_copy("{0}sshd-ubuntu.toml".format(sourcepath+"/conf.extra/"), "$tmplsDir/cfg/core/conf/", recursive=True)
        self._cuisine.core.dir_ensure("$tmplsDir/cfg/core/extensions/syncthing")
        self._cuisine.core.file_copy("$binDir/syncthing", "$tmplsDir/cfg/core/extensions/syncthing/", recursive=True)


        if start:
            self.start(nid, gid)

    def start(self, gid, nid, controller_url="http://127.0.0.1:8966"):
        """
        if this is run on the sam e machine as a controller instance run controller first as the
        core will consume the avialable syncthing port and will cause a problem
        """

        # @todo this will break code if two instances on same machine
        if not nid:
            nid = 1
        if not gid:
            gid = 1

        self._cuisine.core.dir_ensure("$cfgDir/core/")
        self._cuisine.core.file_copy(
            "$tmplsDir/cfg/core", "$cfgDir/", recursive=True)

        # manipulate config file
        sourcepath = "$tmplsDir/cfg/core"
        C = self._cuisine.core.file_read("%s/g8os.toml" % sourcepath)
        cfg = j.data.serializer.toml.loads(C)
        cfgdir = self._cuisine.core.dir_paths['cfgDir']
        cfg["main"]["message_ID_file"] = self._cuisine.core.joinpaths(cfgdir, "/core/.mid")
        cfg["main"]["include"] = self._cuisine.core.joinpaths(cfgdir, "/core/conf")
        cfg["main"].pop("network")
        cfg["controllers"] = {"main": {"url": controller_url}}
        cfg["extension"]["sync"]["cwd"] = self._cuisine.core.joinpaths(cfgdir, "/core/extensions")
        cfg["extension"]["jumpscript"]["cwd"] = self._cuisine.core.joinpaths(cfgdir, "/core/extensions/jumpscript")
        cfg["extension"]["jumpscript_content"]["cwd"] = self._cuisine.core.joinpaths(cfgdir, "/core/extensions/jumpscript")
        cfg["extension"]["js_daemon"]["cwd"] = self._cuisine.core.joinpaths(cfgdir, "/core/extensions/jumpscript")
        cfg["extension"]["js_daemon"]["env"]["JUMPSCRIPTS_HOME"] = self._cuisine.core.joinpaths(cfgdir, "/core/jumpscripts/")
        cfg["logging"]["db"]["address"] = self._cuisine.core.joinpaths(cfgdir, "/core/logs")
        C = j.data.serializer.toml.dumps(cfg)

        self._cuisine.core.file_write("$cfgDir/core/g8os.toml", C, replaceArgs=True)

        self._cuisine.apps.mongodb.start()
        self._cuisine.apps.redis.start()
        print("connection test ok to agentcontroller")
        #@todo (*1*) need to implement to work on node
        env = {}
        env["TMPDIR"] = self._cuisine.core.dir_paths["tmpDir"]
        cmd = "$binDir/core -nid %s -gid %s -c $cfgDir/core/g8os.toml" % (
            nid, gid)
        pm = self._cuisine.processmanager.get("tmux")
        pm.ensure("core", cmd=cmd, path="$cfgDir/core", env=env)
