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


class Caddy:

    def __init__(self, executor, cuisine):
        self.executor = executor
        self.cuisine = cuisine

    @actionrun(action=True)
    def build(self, ssl=False, start=True, dns=None):
        self.cuisine.core.file_download('https://github.com/mholt/caddy/releases/download/v0.8.2/caddy_linux_amd64.tar.gz', '$tmpDir/caddy_linux_amd64.tar.gz')
        self.cuisine.core.run('cd $tmpDir; tar xvf $tmpDir/caddy_linux_amd64.tar.gz')
        self.cuisine.core.file_copy('$tmpDir/caddy', '$binDir')
        self.cuisine.bash.addPath(self.cuisine.core.args_replace("$binDir"), action=True)

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
        C = self.cuisine.core.args_replace(C)
        cpath = self.cuisine.core.args_replace("$tmplsDir/cfg/caddy/caddyfile.conf")
        self.cuisine.core.dir_ensure("$tmplsDir/cfg/caddy")
        self.cuisine.core.dir_ensure("$tmplsDir/cfg/caddy/log/")
        self.cuisine.core.dir_ensure("$tmplsDir/cfg/caddy/www/")
        self.cuisine.core.file_write(cpath, C)

        if start:
            self.start(ssl)

    def start(self, ssl):
        cpath = self.cuisine.core.args_replace("$cfgDir/caddy/caddyfile.conf")
        self.cuisine.core.file_copy("$tmplsDir/cfg/caddy", "$cfgDir/caddy", recursive=True)

        #adjust confguration file
        conf = self.cuisine.core.file_read(cpath)
        conf.replace("$tmplsDir/cfg", "$cfgDir")
        conf = self.cuisine.core.args_replace(conf)
        self.cuisine.core.file_write("$cfgDir/caddy/caddyfile.conf", conf, replaceArgs=True)



        self.cuisine.processmanager.stop("caddy")  # will also kill
        fw = not self.cuisine.core.run("ufw status 2> /dev/null || echo **OK**", die=False, check_is_ok=True )
        if ssl:
            if fw:
                self.cuisine.fw.allowIncoming(443)
                self.cuisine.fw.allowIncoming(80)
                self.cuisine.fw.allowIncoming(22)

            if self.cuisine.process.tcpport_check(80, "") or self.cuisine.process.tcpport_check(443, ""):
                raise RuntimeError("port 80 or 443 are occupied, cannot install caddy")

        else:
            if self.cuisine.process.tcpport_check(80, ""):
                raise RuntimeError("port 80 is occupied, cannot install caddy")

            PORTS = ":80"
            if fw:
                self.cuisine.fw.allowIncoming(80)
                self.cuisine.fw.allowIncoming(22)

        cmd = self.cuisine.bash.cmdGetPath("caddy")
        self.cuisine.processmanager.ensure("caddy", '%s -conf=%s -email=info@greenitglobe.com' % (cmd, cpath))


    def caddyConfig(self,sectionname,config):
        """
        config format see https://caddyserver.com/docs/caddyfile
        """
        raise RuntimeError("needs to be implemented")
