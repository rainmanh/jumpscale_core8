from JumpScale import j


base = j.tools.cuisine._getBaseClass()


class CuisineCockpit(base):

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
        self.cuisine.core.dir_ensure("$JSCFGDIR/cockpit_api")
        j.tools.cuisine.local.core.file_write("$JSCFGDIR/cockpit_api/config.toml", C)

    def install(self, start=True, branch="master"):
        if self.doneGet("install") and not reset:
            return
        self.install_deps()
        self.cuisine.development.git.pullRepo('https://github.com/Jumpscale/jscockpit', branch=branch)
        dir_paths = self.cuisine.core.dir_paths
        self.cuisine.core.dir_ensure('%s/ays_api/' % dir_paths['JSAPPSDIR'])
        self.cuisine.core.file_link('%s/github/jumpscale/jscockpit/api_server' %
                                    dir_paths['CODEDIR'], '%s/ays_api/api_server' % dir_paths['JSAPPSDIR'])
        self.cuisine.core.file_link('%s/github/jumpscale/jscockpit/ays_api' %
                                    dir_paths['CODEDIR'], '%s/ays_api/ays_api' % dir_paths['JSAPPSDIR'])
        self.configure()
        if start:
            self.start()
        self.doneSet("install")

    def install_all_in_one(self, start=True, branch="8.1.0_cleanup", reset=False):
        """
        This will install the all the component of the cockpit in one command.
        (mongodb, portal, ays_api, ays_daemon)

        Make sure that you don't have uncommitted code in any code repository cause this method will discard them !!!
        """

        self.log("Kill all remaining tmux sessions")

        self.cuisine.core.run("killall tmux", die=False)

        # install mongodb, required for portal
        self.cuisine.apps.mongodb.install(start=start, reset=reset)

        # install portal
        self.cuisine.apps.portal.install(start=False, branch=branch, reset=reset)
        # add link from portal to API
        content = self.cuisine.core.file_read(
            '$CODEDIR/github/jumpscale/jumpscale_portal8/apps/portalbase/AYS81/.space/nav.wiki')
        if 'REST API:/api' not in content:
            self.cuisine.core.cuisine.core.file_write('$CODEDIR/github/jumpscale/jumpscale_portal8/apps/portalbase/AYS81/.space/nav.wiki',
                                                      'AYS API:http://localhost:5000/apidocs/index.html?raml=api.raml',
                                                      append=True)

        txt = self.cuisine.core.file_read("$JSCFGDIR/portals/main/config.hrd")
        hrd = j.data.hrd.get(content=txt)
        hrd.prefixWithName = False  # bug in hrd
        hrd.set("param.cfg.production", False)
        self.cuisine.core.file_write("$JSCFGDIR/portals/main/config.hrd", str(hrd))

        self.cuisine.apps.portal.configure(production=False)

        self.cuisine.apps.portal.start()

        # install REST API AND ays daemon
        self.install(start=start, branch=branch)

        # configure base URI for api-console
        raml = self.cuisine.core.file_read('$JSAPPSDIR/ays_api/ays_api/apidocs/api.raml')
        raml = raml.replace('$(baseuri)', "http://localhost:5000")
        self.cuisine.core.file_write('$JSAPPSDIR/ays_api/ays_api/apidocs/api.raml', raml)

        if start:
            # start API and daemon
            self.start()

    def start(self, name='main'):
        # start AYS REST API
        cmd = 'jspython api_server'
        dir_paths = self.cuisine.core.dir_paths
        self.cuisine.processmanager.ensure(cmd=cmd, name='cockpit_%s' %
                                           name,  path='%s/ays_api' % dir_paths['JSAPPSDIR'])

        # start daemon
        cmd = 'ays start'
        self.cuisine.processmanager.ensure(cmd=cmd, name='cockpit_daemon_%s' % name)

    def stop(self, name='main'):
        self.cuisine.processmanager.stop('cockpit_%s' % name,)
        self.cuisine.processmanager.stop('cockpit_daemon_%s' % name,)

    def install_deps(self):
        self.cuisine.package.mdupdate()
        self.cuisine.package.install('libssl-dev')

        deps = """
        cryptography
        python-jose
        wtforms_json
        flask_wtf
        python-telegram-bot
        """
        self.cuisine.development.pip.multiInstall(deps, upgrade=True)
