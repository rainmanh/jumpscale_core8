from JumpScale import j


base = j.tools.cuisine._getBaseClass()


class CuisineCockpit(base):

    def __init__(self, executor, cuisine):
        self._executor = executor
        self._cuisine = cuisine

    def configure(self):
        C = """
        [mode]
        prod = false

        [oauth]
        client_secret = "IqFcD2TYC7WrPpoH2Oi6YTpN102Hj-sdfsdfsdfsdf-sMBcydIacGI"
        redirect_uri = "https://f0919f6e.ngrok.io/oauth/callback"
        client_id = "OrgTest"
        organization = "OrgTest"
        jwt_key = ""

        [api]
        [api.ays]
        port = 5000
        host = "0.0.0.0"
        debug = true
        """
        self._cuisine.core.dir_ensure("$cfgDir/cockpit_api")
        j.tools.cuisine.local.core.file_write("$cfgDir/cockpit_api/config.toml", C)

    def install(self, start=True, branch="master"):
        self.install_deps()
        self._cuisine.development.git.pullRepo('https://github.com/Jumpscale/jscockpit', branch=branch)
        self._cuisine.core.dir_ensure('%s/ays_api/' % j.dirs.appDir)
        self._cuisine.core.file_link('%s/github/jumpscale/jscockpit/api_server' %
                                     j.dirs.codeDir, '%s/ays_api/api_server' % j.dirs.appDir)
        self._cuisine.core.file_link('%s/github/jumpscale/jscockpit/ays_api' %
                                     j.dirs.codeDir, '%s/ays_api/ays_api' % j.dirs.appDir)
        self.configure()
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
        python-jose
        wtforms_json
        flask_wtf
        python-telegram-bot
        """
        self._cuisine.development.pip.multiInstall(deps, upgrade=True)
