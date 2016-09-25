from JumpScale import j


app = j.tools.cuisine._getBaseAppClass()


class CuisineDeployerBot(app):
    NAME = ''

    def isInstalled(self):
        return self._cuisine.core.file_exists(
            "$appDir/deployer_bot/telegram-bot") and self._cuisine.core.file_exists('$cfgDir/deployerbot/config.toml')

    def install(self, start=True, token=None, g8_addresses=None, dns=None, oauth=None):
        """
        Install deployerbot
        If start is True, token g8_addresses, dns and oauth should be specified
        """
        if self.isInstalled():
            return

        self._cuisine.bash.environSet("LC_ALL", "C.UTF-8")
        if not self._cuisine.core.isMac and not self._cuisine.core.isCygwin:
            self._cuisine.development.js8.install()
            self._cuisine.development.pip.packageUpgrade("pip")

        self.install_deps()
        self._cuisine.development.git.pullRepo('https://github.com/Jumpscale/jscockpit.git')
        self.link_code()

        if start:
            self.start(token=token, g8_addresses=g8_addresses, dns=dns, oauth=oauth)

    def start(self, token=None, g8_addresses=None, dns=None, oauth=None):
        """
        token: telegram bot token received from @botfather
        g8_addresses: list of g8 addresses. e.g: ['be-scale-1.demo.greenitglobe.com', 'du-conv-2.demo.greenitglobe.com']
        dns: dict containing login and password e.g: {'login': 'admin', 'password':'secret'}
        oauth: dict containing
               host
               oauth
               client_id
               client_secret
               itsyouonline.host
        see https://github.com/Jumpscale/jscockpit/blob/master/deploy_bot/README.md for example
        """
        self.create_config(token=token, g8_addresses=g8_addresses, dns=dns, oauth=oauth)
        cmd = self._cuisine.core.args_replace(
            'jspython $appDir/deployer_bot/telegram-bot --config $cfgDir/deployerbot/config.toml')
        cwd = self._cuisine.core.args_replace('$appDir/deployer_bot')
        self._cuisine.processmanager.ensure('deployerbot', cmd=cmd, path=cwd)

    def install_deps(self):
        deps = """
        flask
        python-telegram-bot
        """
        self._cuisine.development.pip.multiInstall(deps, upgrade=True)

    def link_code(self):
        self._cuisine.core.dir_ensure("$appDir")
        self._cuisine.core.file_link('$codeDir/github/jumpscale/jscockpit/deployer_bot/', '$appDir/deployer_bot')

    def create_config(self, token=None, g8_addresses=None, dns=None, oauth=None):
        """
        token: telegram bot token received from @botfather
        g8_addresses: list of g8 addresses. e.g: ['be-scale-1.demo.greenitglobe.com', 'du-conv-2.demo.greenitglobe.com']
        dns: dict containing login and password e.g: {'login': 'admin', 'password':'secret'}
        oauth: dict containing
               host
               oauth
               client_id
               client_secret
               itsyouonline.host
        see https://github.com/Jumpscale/jscockpit/blob/master/deploy_bot/README.md for example
        """
        cfg = {
            'bot': {
                'token': token,
            },
            'g8': {},
            'dns': dns,
            'oauth': oauth
        }
        for address in g8_addresses:
            name = address.split('.')[0]
            cfg['g8'][name] = {
                'address': address
            }
        # make sure port is an int
        cfg['oauth']['port'] = int(cfg['oauth']['port'])

        self._cuisine.core.createDir('$cfgDir/deployerbot')
        content = j.data.serializer.toml.dumps(cfg)
        self._cuisine.core.file_write('$cfgDir/deployerbot/config.toml', content)
