from JumpScale import j


from ActionDecorator import ActionDecorator


"""
please ensure that the start and build methods are separate and
the build doesnt place anyfile outside opt as it will be used in aysfs mounted system
"""


class actionrun(ActionDecorator):

    def __init__(self, *args, **kwargs):
        ActionDecorator.__init__(self, *args, **kwargs)
        self.selfobjCode = "cuisine=j.tools.cuisine.getFromId('$id');selfobj=cuisine.apps.caddy"

base = j.tools.cuisine.getBaseClass()


class Caddy(base):

    def __init__(self, executor, cuisine):
        self._executor = executor
        self._cuisine = cuisine

    
    def install(self, ssl=False, start=True, dns=None):
        self._cuisine.core.file_download(
            'https://github.com/mholt/caddy/releases/download/v0.8.2/caddy_linux_amd64.tar.gz', '$tmpDir/caddy_linux_amd64.tar.gz')
        self._cuisine.core.run('cd $tmpDir; tar xvf $tmpDir/caddy_linux_amd64.tar.gz')
        self._cuisine.core.file_copy('$tmpDir/caddy', '$binDir')
        self._cuisine.bash.addPath(self._cuisine.core.args_replace("$binDir"))

        if ssl and dns:
            addr = dns
        else:
            addr = ':80'

        C = """
        $addr
        gzip
        log $tmplsDir/cfg/caddy/log/access.log
        errors {
            log $tmplsDir/cfg/caddy/log/errors.log
        }
        root $tmplsDir/cfg/caddy/www
        """
        C = C.replace("$addr", addr)
        C = self._cuisine.core.args_replace(C)
        cpath = self._cuisine.core.args_replace("$tmplsDir/cfg/caddy/caddyfile.conf")
        self._cuisine.core.dir_ensure("$tmplsDir/cfg/caddy")
        self._cuisine.core.dir_ensure("$tmplsDir/cfg/caddy/log/")
        self._cuisine.core.dir_ensure("$tmplsDir/cfg/caddy/www/")
        self._cuisine.core.file_write(cpath, C)

        if start:
            self.start(ssl)

    
    def start(self, ssl):
        cpath = self._cuisine.core.args_replace("$cfgDir/caddy/caddyfile.conf")
        self._cuisine.core.file_copy("$tmplsDir/cfg/caddy", "$cfgDir/caddy", recursive=True)

        # adjust confguration file
        conf = self._cuisine.core.file_read(cpath)
        conf.replace("$tmplsDir/cfg", "$cfgDir")
        conf = self._cuisine.core.args_replace(conf)
        self._cuisine.core.file_write("$cfgDir/caddy/caddyfile.conf", conf, replaceArgs=True)

        self._cuisine.processmanager.stop("caddy")  # will also kill

        fw = not self._cuisine.core.run("ufw status 2> /dev/null", die=False)[0]

        if ssl:
            # Do if not  "ufw status 2> /dev/null" didn't run properly
            if fw:
                self._cuisine.ufw.allowIncoming(443)
                self._cuisine.ufw.allowIncoming(80)
                self._cuisine.ufw.allowIncoming(22)

            if self._cuisine.process.tcpport_check(80, "") or self._cuisine.process.tcpport_check(443, ""):
                raise RuntimeError("port 80 or 443 are occupied, cannot install caddy")

        else:
            if self._cuisine.process.tcpport_check(80, ""):
                raise RuntimeError("port 80 is occupied, cannot install caddy")

            PORTS = ":80"
            if fw:
                self._cuisine.ufw.allowIncoming(80)
                self._cuisine.ufw.allowIncoming(22)

        cmd = self._cuisine.bash.cmdGetPath("caddy")
        self._cuisine.processmanager.ensure("caddy", '%s -conf=%s -email=info@greenitglobe.com' % (cmd, cpath))

    
    def caddyConfig(self, sectionname, config):
        """
        config format see https://caddyserver.com/docs/caddyfile
        """
        raise RuntimeError("needs to be implemented")
