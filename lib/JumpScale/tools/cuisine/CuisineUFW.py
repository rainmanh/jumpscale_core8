
from JumpScale import j

from ActionDecorator import ActionDecorator
class actionrun(ActionDecorator):
    def __init__(self,*args,**kwargs):
        ActionDecorator.__init__(self,*args,**kwargs)
        self.selfobjCode="cuisine=j.tools.cuisine.getFromId('$id');selfobj=cuisine.ufw"

base=j.tools.cuisine.getBaseClass()
class CuisineUFW(base):

    def __init__(self, executor, cuisine):
        self.executor = executor
        self.cuisine = cuisine
        self._ufw_allow = {}
        self._ufw_deny = {}
        self._ufw_enabled = None

    @property
    def ufw_enabled(self):
        if not self._ufw_enabled:
            if not self.cuisine.core.isMac:
                if self.cuisine.bash.cmdGetPath("ufw", die=False) == False:
                    self.cuisine.package.install("ufw")
                    self.cuisine.bash.cmdGetPath("ufw")
                self._ufw_enabled = not "inactive" in self.cuisine.core.run("ufw status")[1]
        return self._ufw_enabled

    @actionrun(action=True)
    def ufw_enable(self):
        if not self.ufw_enabled:
            if not self.cuisine.core.isMac:
                if self.executor.type != 'local':
                    self.cuisine.core.run("ufw allow %s" % self.executor.port)
                self.cuisine.core.run("echo \"y\" | ufw enable")
                self._ufw_enabled = True
        return True

    @property
    def ufw_rules_allow(self):
        if self.cuisine.core.isMac:
            return {}
        if self._ufw_allow == {}:
            self._ufw_status()
        return self._ufw_allow

    @property
    def ufw_rules_deny(self):
        if self.cuisine.core.isMac:
            return {}
        if self._ufw_deny == {}:
            self._ufw_status()
        return self._ufw_deny

    def _ufw_status(self):
        self.ufw_enable()
        _, out, _ = self.cuisine.core.run("ufw status", action=True, force=True)
        for line in out.splitlines():
            if line.find("(v6)") != -1:
                continue
            if line.find("ALLOW ") != -1:
                ip = line.split(" ", 1)[0]
                self._ufw_allow[ip] = "*"
            if line.find("DENY ") != -1:
                ip = line.split(" ", 1)[0]
                self._ufw_deny[ip] = "*"

    @actionrun(action=True)
    def allowIncoming(self, port, protocol='tcp'):
        if self.cuisine.core.isMac:
            return
        self.ufw_enable()
        self.cuisine.core.run("ufw allow %s/%s" % (port, protocol))

    @actionrun(action=True)
    def denyIncoming(self, port):
        if self.cuisine.core.isMac:
            return

        self.ufw_enable()
        self.cuisine.core.run("ufw deny %s" % port)

    @actionrun(action=True,force=True)
    def flush(self):
        C = """
        ufw disable
        iptables --flush
        iptables --delete-chain
        iptables --table nat --flush
        iptables --table filter --flush
        iptables --table nat --delete-chain
        iptables --table filter --delete-chain
        """
        self.cuisine.core.run_script(C)

    def show(self):
        a = self.ufw_rules_allow
        b = self.ufw_rules_deny
        print("ALLOW")
        print(a)
        print("DENY")
        print(b)

        # print(self.cuisine.core.run("iptables -t nat -nvL"))
