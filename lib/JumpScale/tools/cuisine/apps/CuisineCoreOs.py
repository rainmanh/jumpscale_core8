from JumpScale import j


from ActionDecorator import ActionDecorator


"""
please ensure that the start and build methods are separate and
the build doesnt place anyfile outside opt as it will be used in aysfs mounted system
"""


class actionrun(ActionDecorator):

    def __init__(self, *args, **kwargs):
        ActionDecorator.__init__(self, *args, **kwargs)
        self.selfobjCode = "cuisine=j.tools.cuisine.getFromId('$id');selfobj=cuisine.apps.core"


class Core():

    def __init__(self, executor, cuisine):
        self.executor = executor
        self.cuisine = cuisine

    @actionrun(action=True)
    def build(self, start=True, gid=None, nid=None):
        """
        builds and setsup dependencies of agent to run with the given gid and nid
        neither can be zero
        """
        # deps
        self.cuisine.apps.installdeps()
        self.cuisine.apps.redis.build(start=False)
        self.cuisine.apps.mongodb.build(start=False)
        # self.cuisine.installer.jumpscale8()

        self.cuisine.apps.syncthing.build(start=False)

        self.cuisine.tmux.killWindow("main", "core")

        self.cuisine.process.kill("core")

        self.cuisine.core.dir_ensure("$tmplsDir/cfg/core", recursive=True)
        self.cuisine.core.dir_ensure("$tmplsDir/cfg/core/.mid", recursive=True)

        url = "github.com/g8os/core"
        self.cuisine.golang.godep(url)

        sourcepath = "$goDir/src/github.com/g8os/core"

        self.cuisine.core.run("cd %s && go build ." % sourcepath, profile=True)
        self.cuisine.core.file_move("%s/core" % sourcepath, "$binDir/core")

        # copy extensions
        self.cuisine.core.dir_remove("$tmplsDir/cfg/core/extensions")
        self.cuisine.core.file_copy("%s/extensions" % sourcepath, "$tmplsDir/cfg/core", recursive=True)
        self.cuisine.core.file_copy("%s/agent.toml" % sourcepath, "$tmplsDir/cfg/core")
        self.cuisine.core.file_copy("%s/conf" % sourcepath, "$tmplsDir/cfg/core", recursive=True)
        self.cuisine.core.dir_ensure("$tmplsDir/cfg/core/extensions/syncthing")
        self.cuisine.core.file_copy("$binDir/syncthing", "$tmplsDir/cfg/core/extensions/syncthing/")

        # self.cuisine.core.dir_ensure("$cfgDir/agent8/agent8/conf", recursive=True)

        if start:
            self.start(nid, gid)

    def start(self, nid, gid):
        """
        if this is run on the sam e machine as a controller instance run controller first as the
        core will consume the avialable syncthing port and will cause a problem
        """

        # @todo this will break code if two instances on same machine
        if not nid:
            nid = 1
        if not gid:
            gid = 1

        self.cuisine.core.dir_ensure("$cfgDir/core/")
        self.cuisine.core.file_copy(
            "$tmplsDir/cfg/core", "$cfgDir/", recursive=True)

        # manipulate config file
        sourcepath = "$tmplsDir/cfg/core"
        C = self.cuisine.core.file_read("%s/agent.toml" % sourcepath)
        cfg = j.data.serializer.toml.loads(C)
        cfgdir = self.cuisine.core.dir_paths['cfgDir']
        cfg["main"]["message_ID_file"] = self.cuisine.core.joinpaths(
            cfgdir, "/core/.mid")
        cfg["main"]["include"] = self.cuisine.core.joinpaths(cfgdir, "/core/conf")
        cfg["extensions"]["sync"]["cwd"] = self.cuisine.core.joinpaths(cfgdir, "/core/extensions")
        cfg["extensions"]["jumpscript"]["cwd"] = self.cuisine.core.joinpaths(cfgdir, "/core/extensions/jumpscript")
        cfg["extensions"]["jumpscript_content"]["cwd"] = self.cuisine.core.joinpaths(cfgdir, "/core/extensions/jumpscript")
        cfg["extensions"]["js_daemon"]["cwd"] = self.cuisine.core.joinpaths(cfgdir, "/core/extensions/jumpscript")
        cfg["extensions"]["js_daemon"]["env"]["JUMPSCRIPTS_HOME"] = self.cuisine.core.joinpaths(cfgdir, "/core/jumpscripts/")
        cfg["logging"]["db"]["address"] = self.cuisine.core.joinpaths(cfgdir, "/core/logs")
        C = j.data.serializer.toml.dumps(cfg)

        self.cuisine.core.file_write("$cfgDir/core/agent.toml", C, replaceArgs=True)

        self.cuisine.apps.mongodb.start()
        self.cuisine.apps.redis.start()
        print("connection test ok to agentcontroller")
        #@todo (*1*) need to implement to work on node
        env = {}
        env["TMPDIR"] = self.cuisine.core.dir_paths["tmpDir"]
        cmd = "$binDir/core -nid %s -gid %s -c $cfgDir/core/agent.toml" % (
            nid, gid)
        pm = self.cuisine.processmanager.get("tmux")
        pm.ensure("core", cmd=cmd, path="$cfgDir/core", env=env)
