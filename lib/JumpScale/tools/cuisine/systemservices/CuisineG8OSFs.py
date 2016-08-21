from JumpScale import j

app = j.tools.cuisine._getBaseAppClass()


class CuisineG8OSFs(app):
    """
    fuse based filesystem for our g8OS, but can be used in other context too
    """
    NAME = 'fs'

    def build(self, start=False):
        if self.isInstalled():
            return 
       
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
        #install golang 
        self._cuisine.development.golang.install()

        # self._cuisine.development.golang.install()
        self._cuisine.development.golang.godep("github.com/g8os/fs")
        self._cuisine.core.run("cd %s && go build ." % "$goDir/src/github.com/g8os/fs", profile=True)
        self._cuisine.core.dir_ensure("$tmplsDir/cfg/fs")
        self._cuisine.core.file_copy("$goDir/src/github.com/g8os/fs/fs", "$base/bin")
        self._cuisine.core.file_write("$goDir/src/github.com/g8os/fs/config/config.toml", content)
        self._cuisine.core.file_copy("$goDir/src/github.com/g8os/fs/config/config.toml", "$tmplsDir/cfg/fs")
        self._cuisine.core.file_download(
            "https://stor.jumpscale.org/storx/static/js8_opt.flist", "$tmplsDir/cfg/fs/js8_opt.flist")
        if start:
            self.start()

    def start(self):
        self._cuisine.core.file_copy("$tmplsDir/cfg/fs", "$cfgDir", recursive=True)
        self._cuisine.processmanager.ensure('fs', cmd="$binDir/fs -c $cfgDir/fs/config.toml")
