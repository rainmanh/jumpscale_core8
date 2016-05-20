from JumpScale import j
from ActionDecorator import ActionDecorator


"""
please ensure that the start and build methods are separate and
the build doesnt place anyfile outside opt as it will be used in aysfs mounted system
"""


class actionrun(ActionDecorator):

    def __init__(self, *args, **kwargs):
        ActionDecorator.__init__(self, *args, **kwargs)
        self.selfobjCode = "cuisine=j.tools.cuisine.getFromId('$id');selfobj=cuisine.apps.cockpit"


class Cockpit():

    def __init__(self, executor, cuisine):
        self.executor = executor
        self.cuisine = cuisine

    @actionrun(action=True)
    def build(self, start=True, bot_token='', jwt_key='', organization=''):
        """
        Build and Install cockpit
        If start is True, bot_token, jwt_key, organization should be specified
        """
        self.cuisine.bash.environSet("LC_ALL", "C.UTF-8")
        if not self.cuisine.core.isMac:
            self.cuisine.installerdevelop.jumpscale8()
            self.cuisine.pip.upgrade("pip")

        self.installDeps()
        self.cuisine.git.pullRepo('https://github.com/Jumpscale/jscockpit.git')
        self.link_code()

        if start:
            self.start(bot_token, jwt_key, organization)

    def start(self, bot_token, jwt_key, organization):
        """
        bot_token: telegram token for cockpit bot
        """
        self.create_config(bot_token, jwt_key, organization)
        cmd = 'jspython cockpit --config $cfgDir/cockpit/config.toml'
        self.cuisine.processmanager.ensure('cockpit', cmd=cmd, path='/opt/jumpscale8/apps/cockpit')

    def install_deps(self):
        deps = """
        cryptography
        pyjwt
        wtforms_json
        flask_wtf
        python-telegram-bot
        """
        self.cuisine.pip.multiInstall(deps, update=True)

    def link_code(self):
        self.cuisine.core.file_link('$codeDir/github/jumpscale/jscockpit/app/', '$appDir/cockpit')

    def create_config(self, bot_token, jwt_key, organization):
        cfg = {
            'api': {
                'ays': {
                    'host': 'localhost',
                    'port': 5000,
                    'active': True,
                    'jwt_key': jwt_key,
                    'organization': organization
                }
            },
            'bot': {
                'token': bot_token,
            },
            'mail': {
                'port': 25
            }
        }
        self.cuisine.core.createDir('$cfgDir/cockpit')
        content = j.data.serializer.toml.dumps(cfg)
        self.cuisine.core.file_write('$cfgDir/cockpit/config.toml', content)
