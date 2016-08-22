from JumpScale import j


base = j.tools.cuisine._getBaseClass()


class CuisineCockpit(base):

    def __init__(self, executor, cuisine):
        self._executor = executor
        self._cuisine = cuisine

    def build(self, start=True, bot_token='', jwt_key='', organization='', client_secret='', client_id='', redirect_uri='', itsyouonlinehost='https://itsyou.online'):
        """
        Build and Install cockpit
        If start is True, bot_token, jwt_key, organization should be specified
        """
        self._cuisine.bash.environSet("LC_ALL", "C.UTF-8")
        # if not self._cuisine.core.isMac and not self._cuisine.core.isCygwin:
        #     self._cuisine.installerdevelop.jumpscale8()
        #     self._cuisine.development.pip.upgrade("pip")

        self.install_deps()
        self._cuisine.development.git.pullRepo('https://github.com/Jumpscale/jscockpit.git')
        self.link_code()

        if start:
            self.start(bot_token, jwt_key, organization, client_secret, client_id, redirect_uri, itsyouonlinehost)

    def start(self, bot_token='', jwt_key='', organization='', client_secret='', client_id='', redirect_uri='', itsyouonlinehost='https://itsyou.online'):
        """
        bot_token: telegram token for cockpit bot
        """
        self.create_config(bot_token, jwt_key, organization, client_secret, client_id, redirect_uri, itsyouonlinehost)
        cmd = 'jspython cockpit start --config $cfgDir/cockpit/config.toml'
        self._cuisine.processmanager.ensure('cockpit', cmd=cmd, path='/opt/jumpscale8/apps/cockpit')

    def install_deps(self):
        deps = """
        cryptography
        pyjwt
        wtforms_json
        flask_wtf
        python-telegram-bot
        """
        self._cuisine.development.pip.multiInstall(deps, upgrade=True)

    def link_code(self):
        self._cuisine.core.file_link('$codeDir/github/jumpscale/jscockpit/jscockpit/', '$appDir/cockpit')

    def create_config(self, bot_token, jwt_key, organization, client_secret, client_id, redirect_uri, itsyouonlinehost='https://itsyou.online'):
        cfg = {
            'oauth': {
                'client_secret': client_secret,
                'client_id': client_id,
                'redirect_uri': redirect_uri,
                'organization': organization,
                'jwt_key': jwt_key,
                'itsyouonlinehost': itsyouonlinehost,
            },
            'api': {
                'ays': {
                    'host': 'localhost',
                    'port': 5000,
                    'active': True,
                }
            },
            'bot': {
                'token': bot_token,
                'active': True,
            },
            'mail': {
                'port': 25,
                'active': True,
            }
        }
        self._cuisine.core.createDir('$cfgDir/cockpit')
        content = j.data.serializer.toml.dumps(cfg)
        self._cuisine.core.file_write('$cfgDir/cockpit/config.toml', content)
