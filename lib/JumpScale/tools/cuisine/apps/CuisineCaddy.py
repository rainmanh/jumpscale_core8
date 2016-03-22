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


class Caddy():

    def __init__(self, executor, cuisine):
        self.executor = executor
        self.cuisine = cuisine

    @actionrun(action=True)
    def build(self, ssl=False, start=True, dns=None):
        self.cuisine.golang.install()
        self.cuisine.golang.get("github.com/mholt/caddy", action=True)
        self.cuisine.core.file_copy(self.cuisine.core.joinpaths('$goDir', 'bin', 'caddy'), '$binDir', action=True)
        self.cuisine.bash.addPath(self.cuisine.core.args_replace("$binDir"), action=True)

        if ssl and dns:
            addr = dns
        else:
            addr = ':80'

        C = """
        $addr
        gzip
        log $cfgDir/caddy/log/access.log
        errors {
            log $cfgDir/caddy/log/errors.log
        }
        root $cfgDir/caddy/www
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
        cpath = self.cuisine.core.args_replace("$tmplsDir/cfg/caddy/caddyfile.conf")
        self.cuisine.processmanager.stop("caddy")  # will also kill
        if ssl:
            self.cuisine.fw.allowIncoming(443)
            self.cuisine.fw.allowIncoming(80)

            if self.cuisine.process.tcpport_check(80, "") or self.cuisine.process.tcpport_check(443, ""):
                raise RuntimeError("port 80 or 443 are occupied, cannot install caddy")

        else:
            if self.cuisine.process.tcpport_check(80, ""):
                raise RuntimeError("port 80 is occupied, cannot install caddy")

            PORTS = ":80"
            self.cuisine.fw.allowIncoming(80)
        cmd = self.cuisine.bash.cmdGetPath("caddy")
        self.cuisine.processmanager.ensure("caddy", '%s -conf=%s -email=info@greenitglobe.com' % (cmd, cpath))


    def caddyConfig(self,sectionname,config):
        """
        config format see https://caddyserver.com/docs/caddyfile
        """
        raise RuntimeError("needs to be implemented")
