from JumpScale import j


app = j.tools.cuisine._getBaseAppClass()


class CuisineSkyDns(app):
    NAME = "skydns"
    def __init__(self, executor, cuisine):
        self._executor = executor
        self._cuisine = cuisine

    def build(self, start=True, install=True):
        if self.isInstalled():
            return
        self._cuisine.development.golang.install()
        self._cuisine.development.golang.get("github.com/skynetservices/skydns")
        if install:
            self.install(start)

    def install(self, start=True):
        """
        download , install, move files to appropriate places, and create relavent configs 
        """
        self._cuisine.core.file_copy(self._cuisine.core.joinpaths('$goDir', 'bin', 'skydns'), '$binDir')
        self._cuisine.bash.addPath(self._cuisine.core.args_replace("$binDir"))

        if start:
            self.start()

    def start(self):
        cmd = self._cuisine.bash.cmdGetPath("skydns")
        self._cuisine.processmanager.ensure("skydns", cmd + " -addr 0.0.0.0:53")
