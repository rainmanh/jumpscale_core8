from JumpScale import j


from ActionDecorator import ActionDecorator


"""
please ensure that the start and build methods are separate and
the build doesnt place anyfile outside opt as it will be used in aysfs mounted system
"""


class actionrun(ActionDecorator):

    def __init__(self, *args, **kwargs):
        ActionDecorator.__init__(self, *args, **kwargs)
        self.selfobjCode = "cuisine=j.tools.cuisine.getFromId('$id');selfobj=cuisine.apps.fs"


class Fs():

    def __init__(self, executor, cuisine):
        self.executor = executor
        self.cuisine = cuisine

    @actionrun(action=True)
    def build(self, start=False):
        content = """
        [[mount]]
            path="/opt"
            flist="/optvar/cfg/fs/js8_opt.flist"
            backend="opt"
            mode="RO"
            trim_base=true
        [backend]
        [backend.opt]
            path="/optvar/fs_backend/opt"
            stor="public"
            namespace="js8_opt"
            cleanup_cron="@every 1h"
            cleanup_older_than=24
            log=""
        [aydostor]
        [aydostor.public]
            addr="http://stor.jumpscale.org/storx"
            login=""
            passwd=""
        """
        self.cuisine.golang.install()
        self.cuisine.golang.get("github.com/g8os/fs", action=True)
        self.cuisine.core.dir_ensure("$tmplsDir/cfg/fs")
        self.cuisine.core.file_copy("$goDir/bin/fs", "$base/bin")
        self.cuisine.core.file_write("$goDir/src/github.com/g8os/fs/config/config.toml", content)
        self.cuisine.core.file_copy("$goDir/src/github.com/g8os/fs/config/config.toml", "$tmplsDir/cfg/fs")
        if start:
            self.start()

    def start(self):
        self.cuisine.core.file_copy("$tmplsDir/cfg/fs", "$cfgDir", recursive=True)
        self.cuisine.processmanager.ensure('fs', cmd="$binDir/fs -c $cfgDir/fs/config.toml")