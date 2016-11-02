from JumpScale import j


base = j.tools.cuisine._getBaseClass()


class CuisineCockpit(base):

    def __init__(self, executor, cuisine):
        self._executor = executor
        self._cuisine = cuisine

    def install(self, start=True):
        self.install_deps()
        self._cuisine.development.git.pullRepo('https://github.com/Jumpscale/jscockpit')
        self._cuisine.core.dir_ensure('%s/ays_api/' % j.dirs.appDir)
        self._cuisine.core.file_copy('%s/github/jumpscale/jscockpit/jscockpit/api_server' % j.dirs.codeDir, '%s/ays_api/api_server' % j.dirs.appDir)
        self._cuisine.core.file_copy('%s/github/jumpscale/jscockpit/jscockpit/ays_api' % j.dirs.codeDir, '%s/ays_api/ays_api' % j.dirs.appDir, recursive=True)
        if start:
            self.start()

    def start(self, name='cockpit'):
        cmd = 'jspython api_server'
        self._cuisine.processmanager.ensure('cockpit', cmd=cmd, path='%s/ays_api' % j.dirs.appDir)

    def install_deps(self):
        self._cuisine.package.mdupdate()
        self._cuisine.package.install('libssl-dev')

        deps = """
        cryptography
        pyjwt
        wtforms_json
        flask_wtf
        python-telegram-bot
        """
        self._cuisine.development.pip.multiInstall(deps, upgrade=True)
