from JumpScale import j


base = j.tools.cuisine._getBaseClass()


class CuisineCockpit(base):

    def __init__(self, executor, cuisine):
        self._executor = executor
        self._cuisine = cuisine

    def install(self, start=True):
        self.install_deps()
        self._cuisine.development.git.pullRepo('https://github.com/Jumpscale/jscockpit', ssh=False)
        self._cuisine.core.dir_ensure('/opt/jumpscale8/apps/ays_api/')
        self._cuisine.core.file_copy('/opt/code/github/jumpscale/jscockpit/api_server/', '/opt/jumpscale8/apps/ays_api/api_server')
        self._cuisine.core.file_copy('/opt/code/github/jumpscale/jscockpit/ays_api/', '/opt/jumpscale8/apps/ays_api/ays_api', recursive=True)
        if start:
            self.start()

    def start(self, name='cockpit'):
        cmd = 'jspython api_server'
        self._cuisine.processmanager.ensure('cockpit', cmd=cmd, path='/opt/jumpscale8/apps/ays_api')

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
