from JumpScale import j


from ActionDecorator import ActionDecorator


"""
please ensure that the start and build methods are separate and
the build doesnt place anyfile outside opt as it will be used in aysfs mounted system
"""


class actionrun(ActionDecorator):

    def __init__(self, *args, **kwargs):
        ActionDecorator.__init__(self, *args, **kwargs)
        self.selfobjCode = "cuisine=j.tools.cuisine.getFromId('$id');selfobj=cuisine.apps.stor"

base = j.tools.cuisine.getBaseClass()


class AydoStor(base):

    def __init__(self, executor, cuisine):
        self.executor = executor
        self.cuisine = cuisine

    @actionrun(action=True)
    def build(self, addr='0.0.0.0:8090', backend="$varDir/aydostor", start=True):
        """
        Build and Install aydostore
        @input addr, address and port on which the service need to listen. e.g. : 0.0.0.0:8090
        @input backend, directory where to save the data push to the store
        """
        self.cuisine.core.dir_remove("%s/src" % self.cuisine.bash.environGet('GOPATH'))
        self.cuisine.golang.install()
        self.cuisine.golang.get("github.com/g8os/stor", action=True)
        self.cuisine.core.file_copy(self.cuisine.core.joinpaths(
            self.cuisine.core.dir_paths['goDir'], 'bin', 'stor'), '$base/bin', overwrite=True)
        self.cuisine.bash.addPath("$base/bin")

        self.cuisine.processmanager.stop("stor")  # will also kill

        self.cuisine.core.dir_ensure("$cfgDir/stor")
        backend = self.cuisine.core.args_replace(backend)
        self.cuisine.core.dir_ensure(backend)
        config = {
            'listen_addr': addr,
            'store_root': backend,
        }
        content = j.data.serializer.toml.dumps(config)
        self.cuisine.core.file_write("$tmplsDir/cfg/stor/config.toml", content)

        if start:
            self.start(addr)

    @actionrun(force=True)
    def start(self, addr):
        res = addr.split(":")
        if len(res) == 2:
            addr, port = res[0], res[1]
        else:
            addr, port = res[0], '8090'

            self.cuisine.ufw.allowIncoming(port)
            if self.cuisine.process.tcpport_check(port, ""):
                raise RuntimeError(
                    "port %d is occupied, cannot start stor" % port)

        self.cuisine.core.dir_ensure("$cfgDir/stor/", recursive=True)
        self.cuisine.core.file_copy("$tmplsDir/cfg/stor/config.toml", "$cfgDir/stor/")
        cmd = self.cuisine.bash.cmdGetPath("stor")
        self.cuisine.processmanager.ensure("stor", '%s --config $cfgDir/stor/config.toml' % cmd)
