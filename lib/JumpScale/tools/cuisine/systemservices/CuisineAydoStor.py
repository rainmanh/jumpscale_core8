from JumpScale import j


app = j.tools.cuisine._getBaseAppClass()

# TODO: is this still correct, maybe our docker approach better, need to check


class CuisineAydoStor(app):

    NAME = 'stor'
    
    def __init__(self, executor, cuisine):
        self._executor = executor
        self._cuisine = cuisine

    def build(self, addr='0.0.0.0:8090', backend="$varDir/aydostor", start=True, install=True, reset=False):
        """
        Build and Install aydostore
        @input addr, address and port on which the service need to listen. e.g. : 0.0.0.0:8090
        @input backend, directory where to save the data push to the store
        """
        if self.isInstalled() and not reset:
            print('Aydostor is already installed, pass reinstall=True parameter to reinstall')
            return

        self._cuisine.core.dir_remove("%s/src" % self._cuisine.bash.environGet('GOPATH'))
        self._cuisine.development.golang.install()
        self._cuisine.development.golang.get("github.com/g8os/stor")

        if install:
            self.install(addr, backend, start)

    def install(self, addr='0.0.0.0:8090', backend="$varDir/aydostor", start=True):
        """
        download, install, move files to appropriate places, and create relavent configs
        """
        self._cuisine.core.file_copy(self._cuisine.core.joinpaths(
            self._cuisine.core.dir_paths['goDir'], 'bin', 'stor'), '$base/bin', overwrite=True)
        self._cuisine.bash.addPath("$base/bin")

        self._cuisine.processmanager.stop("stor")  # will also kill

        self._cuisine.core.dir_ensure("$cfgDir/stor")
        backend = self._cuisine.core.args_replace(backend)
        self._cuisine.core.dir_ensure(backend)
        config = {
            'listen_addr': addr,
            'store_root': backend,
        }
        content = j.data.serializer.toml.dumps(config)
        self._cuisine.core.dir_ensure('$tmplsDir/cfg/stor', recursive=True)
        self._cuisine.core.file_write("$tmplsDir/cfg/stor/config.toml", content)

        if start:
            self.start(addr)

    def start(self, addr):
        res = addr.split(":")
        if len(res) == 2:
            addr, port = res[0], res[1]
        else:
            addr, port = res[0], '8090'

            self._cuisine.ufw.allowIncoming(port)
            if self._cuisine.process.tcpport_check(port, ""):
                raise RuntimeError(
                    "port %d is occupied, cannot start stor" % port)

        self._cuisine.core.dir_ensure("$cfgDir/stor/", recursive=True)
        self._cuisine.core.file_copy("$tmplsDir/cfg/stor/config.toml", "$cfgDir/stor/")
        cmd = self._cuisine.bash.cmdGetPath("stor")
        self._cuisine.processmanager.ensure("stor", '%s --config $cfgDir/stor/config.toml' % cmd)
