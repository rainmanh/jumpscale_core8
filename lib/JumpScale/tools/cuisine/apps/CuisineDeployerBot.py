from JumpScale import j
from ActionDecorator import ActionDecorator


"""
please ensure that the start and build methods are separate and
the build doesnt place anyfile outside opt as it will be used in aysfs mounted system
"""


class actionrun(ActionDecorator):

    def __init__(self, *args, **kwargs):
        ActionDecorator.__init__(self, *args, **kwargs)
        self.selfobjCode = "cuisine=j.tools.cuisine.getFromId('$id');selfobj=cuisine.apps.deployerbot"

base=j.tools.cuisine.getBaseClass()
class DeployerBot(base):

    @actionrun(action=True)
    def build(self, start=True, token=None, g8_addresses=None, dns=None, oauth=None):
        """
        Build and Install deployerbot
        If start is True, token g8_addresses, dns and oauth should be specified
        """
        self.cuisine.bash.environSet("LC_ALL", "C.UTF-8")
        if not self.cuisine.core.isMac and not self.cuisine.core.isCygwin:
            self.cuisine.installerdevelop.jumpscale8()
            self.cuisine.pip.upgrade("pip")

        self.install_deps()
        self.cuisine.git.pullRepo('https://github.com/Jumpscale/jscockpit.git')
        self.link_code()

        if start:
            self.start(token=token, g8_addresses=g8_addresses, dns=dns, oauth=oauth)

    @actionrun(force=True)
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
        cmd = self.cuisine.core.args_replace('jspython $appDir/deployer_bot/telegram-bot --config $cfgDir/deployerbot/config.toml')
        cwd = self.cuisine.core.args_replace('$appDir/deployer_bot')
        self.cuisine.processmanager.ensure('deployerbot', cmd=cmd, path=cwd)

    @actionrun()
    def install_deps(self):
        deps = """
        flask
        python-telegram-bot
        """
        self.cuisine.pip.multiInstall(deps, upgrade=True)

    @actionrun()
    def link_code(self):
        self.cuisine.core.file_link('$codeDir/github/jumpscale/jscockpit/deploy_bot/', '$appDir/deployer_bot')

    @actionrun()
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

        self.cuisine.core.createDir('$cfgDir/deployerbot')
        content = j.data.serializer.toml.dumps(cfg)
        self.cuisine.core.file_write('$cfgDir/deployerbot/config.toml', content)
