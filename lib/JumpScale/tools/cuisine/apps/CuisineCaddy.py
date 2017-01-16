from JumpScale import j


app = j.tools.cuisine._getBaseAppClass()


class CuisineCaddy(app):

    NAME = "caddy"

    @property
    def builddir(self):
        return j.sal.fs.joinPaths(self.core.dir_paths['BUILDDIR'], "caddy")

    def install(self, ssl=False, start=True, dns=None, reset=False):
        """
        Move binaries and required configs to assigned location.

        @param ssl str:  this tells the firewall to allow port 443 as well as 80 and 22 to support ssl.
        @param start bool: after installing the service this option is true will add the service to the default proccess manager an strart it .
        @param dns str: default address to run caddy on.
        @param reset bool:  if True this will install even if the service is already installed.
        """
        if self.doneGet('install') and reset is False and self.isInstalled():
            return

        os = 'darwin' if self.core.isMac else 'linux'

        if self.core.isMac:
            caddy_url = 'https://github.com/mholt/caddy/releases/download/v0.9.4/caddy_%s_amd64.zip' % os
            dest = j.sal.fs.joinPaths(self.builddir, 'caddy_%s_amd64.zip' % os)
            self.cuisine.core.file_download(caddy_url, dest, minsizekb=4)
            self.cuisine.core.run('cd {builddir}; unzip  -u {builddir}/caddy_{os}_amd64.zip'.format(builddir=self.builddir, os=os))
        else:
            caddy_url = 'https://github.com/mholt/caddy/releases/download/v0.9.4/caddy_%s_amd64.tar.gz' % os
            dest = j.sal.fs.joinPaths(self.builddir, 'caddy_%s_amd64.tar.gz' % os)
            self.cuisine.core.file_download(caddy_url, dest, minsizekb=4)
            self.cuisine.core.run('cd {builddir}; tar xvf {builddir}/caddy_{os}_amd64.tar.gz'.format(builddir=self.builddir, os=os))
        self.cuisine.core.file_copy('{builddir}/caddy_{os}_amd64'.format(builddir=self.builddir, os=os), '$BINDIR/caddy')
        self.cuisine.bash.profileDefault.addPath(self.cuisine.core.dir_paths['BINDIR'])
        self.cuisine.bash.profileDefault.save()
        addr = ':8000'
        if  not self.core.isMac:
            addr = dns if ssl and dns else ':80'

        C = """
        $addr
        gzip
        log $TEMPLATEDIR/cfg/caddy/log/access.log
        errors {
            log $TEMPLATEDIR/cfg/caddy/log/errors.log
        }
        root $TEMPLATEDIR/cfg/caddy/www
        """
        C = C.replace("$addr", addr)
        C = self.replace(C)
        cpath = self.replace("$TEMPLATEDIR/cfg/caddy/caddyfile.conf")
        self.cuisine.core.dir_ensure("$TEMPLATEDIR/cfg/caddy")
        self.cuisine.core.dir_ensure("$TEMPLATEDIR/cfg/caddy/log/")
        self.cuisine.core.dir_ensure("$TEMPLATEDIR/cfg/caddy/www/")
        self.cuisine.core.file_write(cpath, C)

        self.doneSet('install')

        if start:
            self.start(ssl)

    def start(self, ssl):
        cpath = self.replace("$JSCFGDIR/caddy/caddyfile.conf")
        self.cuisine.core.file_copy("$TEMPLATEDIR/cfg/caddy", "$JSCFGDIR/caddy", recursive=True)

        # adjust confguration file
        conf = self.cuisine.core.file_read(cpath)
        conf.replace("$TEMPLATEDIR/cfg", "$JSCFGDIR")
        conf = self.replace(conf)
        self.cuisine.core.file_write("$JSCFGDIR/caddy/caddyfile.conf", conf, replaceArgs=True)

        self.cuisine.processmanager.stop("caddy")  # will also kill

        fw = not self.cuisine.core.run("ufw status 2> /dev/null", die=False)[0]

        if ssl:
            # Do if not  "ufw status 2> /dev/null" didn't run properly
            if fw:
                self.cuisine.systemservices.ufw.allowIncoming(443)
                self.cuisine.systemservices.ufw.allowIncoming(80)
                self.cuisine.systemservices.ufw.allowIncoming(22)

            if self.cuisine.process.tcpport_check(80, "") or self.cuisine.process.tcpport_check(443, ""):
                raise RuntimeError("port 80 or 443 are occupied, cannot install caddy")

        else:
            if self.cuisine.process.tcpport_check(80, ""):
                raise RuntimeError("port 80 is occupied, cannot install caddy")

            PORTS = ":80"
            if fw:
                self.cuisine.systemservices.ufw.allowIncoming(80)
                self.cuisine.systemservices.ufw.allowIncoming(22)

        cmd = self.cuisine.bash.cmdGetPath("caddy")
        self.cuisine.processmanager.ensure("caddy", '%s -conf=%s -email=info@greenitglobe.com' % (cmd, cpath))

    def caddyConfig(self, sectionname, config):
        """
        config format see https://caddyserver.com/docs/caddyfile
        """
        raise RuntimeError("needs to be implemented")
