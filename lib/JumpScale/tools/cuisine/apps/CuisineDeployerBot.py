from JumpScale import j


app = j.tools.cuisine._getBaseAppClass()


class CuisineDeployerBot(app):
    NAME = ''

    def isInstalled(self):
        return self._cuisine.core.file_exists(
            "$appDir/deployer_bot/telegram-bot") and self._cuisine.core.file_exists('$cfgDir/deployerbot/config.toml')

    def install(self, start=True, token=None, g8_addresses=None, dns=None, oauth=None, ays_conf=None):
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
            self.start(token=token, g8_addresses=g8_addresses, dns=dns, oauth=oauth, ays_conf=ays_conf)

    def start(self, token=None, g8_addresses=None, dns=None, oauth=None, ays_conf=None):
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
        db: dict containing
                host
                port
                unixsocket
        see https://github.com/Jumpscale/jscockpit/blob/master/deploy_bot/README.md for example
        """
        self.ays_config(ays_conf)
        self.create_config(token=token, g8_addresses=g8_addresses, dns=dns, oauth=oauth)
        cmd = self._cuisine.core.args_replace(
            'jspython $appDir/deployer_bot/telegram-bot --config $cfgDir/deployerbot/config.yaml')
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

    def ays_config(self, ays_conf=None):
        ays_conf = ays_conf or {}
        AYS_CONFIG_PATH = "$cfgDir/ays/ays.conf"
        REDIS_SOCKET_PATH = "/tmp/redis.sock"

        conf = {
            "redis": {
                "host": ays_conf.get('host', None),
                "port": ays_conf.get('port', None),
                "unixsocket": None if ays_conf.get('host', None) else REDIS_SOCKET_PATH,
            },
            "metadata": {
                "jumpscale": {
                    "url": "https://github.com/Jumpscale/ays_jumpscale8",
                    "branch": "master"
                }
            }
        }
        content = j.data.serializer.yaml.dumps(conf)
        self._cuisine.core.dir_ensure(j.sal.fs.getDirName(AYS_CONFIG_PATH))
        self._cuisine.core.file_write(location=AYS_CONFIG_PATH, content=content, replaceArgs=True)

    def create_config(self, token=None, g8_addresses=None, dns=None, oauth=None):
        """
        token: telegram bot token received from @botfather
        g8_addresses: list of g8 addresses. e.g: ['be-scale-1.demo.greenitglobe.com', 'du-conv-2.demo.greenitglobe.com']
        dns: str dns key path
        oauth: dict containing
               host
               oauth
               client_id
               client_secret
               itsyouonline.host
        see https://github.com/Jumpscale/jscockpit/blob/master/deploy_bot/README.md for example
        """
        g8_addresses = g8_addresses or {}
        oauth = oauth or {}
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
        if cfg['oauth'].get('port', None):
            # make sure port is an int
            cfg['oauth']['port'] = int(cfg['oauth']['port'])

        self._cuisine.core.createDir('$cfgDir/deployerbot')
        content = j.data.serializer.yaml.dumps(cfg)
        self._cuisine.core.file_write('$cfgDir/deployerbot/config.yaml', content)
