from JumpScale import j


app = j.tools.cuisine._getBaseAppClass()


class CuisineController(app):
    NAME = "controller"

    def __init__(self, executor, cuisine):
        self._executor = executor
        self._cuisine = cuisine

    def build(self, start=True, listen_addr=[], install=True, reset=False):
        """
        config: https://github.com/g8os/controller.git
        """
        if reset is False and self.isInstalled():
            return
        # deps
        self._cuisine.apps.redis.install()
        self._cuisine.apps.redis.start()
        self._cuisine.apps.mongodb.build(start=False)
        self._cuisine.apps.syncthing.build(start=False)

        self._cuisine.processmanager.remove("agentcontroller8")
        pm = self._cuisine.processmanager.get("tmux")
        pm.stop("syncthing")

        self._cuisine.core.dir_ensure("$tmplsDir/cfg/controller", recursive=True)

        # get repo
        url = "github.com/g8os/controller"
        self._cuisine.development.golang.clean_src_path()
        self._cuisine.development.golang.godep(url)

        # Do the actual building
        self._cuisine.core.run("cd $goDir/src/github.com/g8os/controller && go build .", profile=True)

        if install:
            self.install(start, listen_addr)

    def install(self, start=True, listen_addr=[]):
        """
        download, install, move files to appropriate places, and create relavent configs
        """
        sourcepath = "$goDir/src/github.com/g8os/controller"
        # move binary
        if not self._cuisine.core.file_exists('$binDir/controller'):
            self._cuisine.core.file_move("%s/controller" % sourcepath, "$binDir/controller")

        # file copy
        self._cuisine.core.dir_remove("$tmplsDir/cfg/controller/extensions")
        self._cuisine.core.file_copy("%s/github/jumpscale/jumpscale_core8/apps/agentcontroller/jumpscripts/jumpscale" %
                                     self._cuisine.core.dir_paths["codeDir"], "$tmplsDir/cfg/controller/jumpscripts/", recursive=True)
        self._cuisine.core.file_copy("%s/extensions" % sourcepath,
                                     "$tmplsDir/cfg/controller/extensions", recursive=True)
        self._cuisine.core.file_copy("%s/agentcontroller.toml" % sourcepath,
                                     '$tmplsDir/cfg/controller/agentcontroller.toml')

        if start:
            self.start(listen_addr=listen_addr)

    def start(self, listen_addr=[]):
        """
        @param listen_addr list of addresse on which the REST API of the controller should listen to
        e.g: [':80', '127.0.0.1:888']
        """
        import hashlib
        from xml.etree import ElementTree

        self._cuisine.core.dir_ensure("$cfgDir/controller/")
        self._cuisine.core.file_copy("$tmplsDir/cfg/controller", "$cfgDir/", recursive=True, overwrite=True)

        # edit config
        C = self._cuisine.core.file_read('$cfgDir/controller/agentcontroller.toml')
        cfg = j.data.serializer.toml.loads(C)

        listen = cfg['listen']
        for addr in listen_addr:
            listen.append({'address': addr})

        cfgDir = self._cuisine.core.dir_paths['cfgDir']
        cfg["events"]["python_path"] = self._cuisine.core.joinpaths(
            cfgDir, "/controller/extensions:/opt/jumpscale8/lib")
        cfg['events']['enabled'] = True
        cfg["processor"]["python_path"] = self._cuisine.core.joinpaths(
            cfgDir, "/controller/extensions:/opt/jumpscale8/lib")
        cfg["jumpscripts"]["python_path"] = self._cuisine.core.joinpaths(
            cfgDir, "/controller/extensions:/opt/jumpscale8/lib")
        cfg["jumpscripts"]["settings"]["jumpscripts_path"] = self._cuisine.core.joinpaths(
            cfgDir, "/controller/jumpscripts")
        C = j.data.serializer.toml.dumps(cfg)

        self._cuisine.core.file_write('$cfgDir/controller/agentcontroller.toml', C, replaceArgs=True)

        # expose syncthing and get api key
        sync_cfg = ElementTree.fromstring(self._cuisine.core.file_read("$tmplsDir/cfg/syncthing/config.xml"))
        sync_id = sync_cfg.find('device').get('id')

        # set address
        sync_cfg.find("./gui/address").text = '127.0.0.1:18384'

        jumpscripts_id = "jumpscripts-%s" % hashlib.md5(sync_id.encode()).hexdigest()
        jumpscripts_path = self._cuisine.core.args_replace("$cfgDir/controller/jumpscripts")

        # find folder element
        configured = False
        for folder in sync_cfg.findall('folder'):
            if folder.get('id') == jumpscripts_id:
                configured = True
                break

        if not configured:
            folder = ElementTree.SubElement(sync_cfg, 'folder', {
                'id': jumpscripts_id,
                'path': jumpscripts_path,
                'ro': 'true',
                'rescanIntervalS': '60',
                'ignorePerms': 'false',
                'autoNormalize': 'false'
            })

            ElementTree.SubElement(folder, 'device', {'id': sync_id})
            ElementTree.SubElement(folder, 'minDiskFreePct').text = '1'
            ElementTree.SubElement(folder, 'versioning')
            ElementTree.SubElement(folder, 'copiers').text = '0'
            ElementTree.SubElement(folder, 'pullers').text = '0'
            ElementTree.SubElement(folder, 'hashers').text = '0'
            ElementTree.SubElement(folder, 'order').text = 'random'
            ElementTree.SubElement(folder, 'ignoreDelete').text = 'false'

        dump = ElementTree.tostring(sync_cfg, 'unicode')
        j.logger.log("SYNCTHING CONFIG", level=10)
        j.logger.log(dump, level=10)
        self._cuisine.core.file_write("$cfgDir/syncthing/config.xml", dump)

        # start
        self._cuisine.apps.syncthing.start()
        self._cuisine.apps.mongodb.start()
        self._cuisine.apps.redis.start()
        env = {}
        env["TMPDIR"] = self._cuisine.core.dir_paths["tmpDir"]
        cmd = "$binDir/controller -c $cfgDir/controller/agentcontroller.toml"
        pm = self._cuisine.processmanager.get("tmux")
        pm.ensure("controller", cmd=cmd, path="$cfgDir/controller/", env=env)
