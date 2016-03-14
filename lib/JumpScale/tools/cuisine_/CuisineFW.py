
from JumpScale import j


class CuisineFW():

    def __init__(self, executor, cuisine):
        self.executor = executor
        self.cuisine = cuisine
        self._ufw_allow = {}
        self._ufw_deny = {}
        self._ufw_enabled = None

    @property
    def ufw_enabled(self):
        if self._ufw_enabled == None:
            if not self.cuisine.isMac:
                if self.cuisine.bash.cmdGetPath("ufw", die=False) == False:
                    self.cuisine.package.install("ufw")
                    self.cuisine.bash.cmdGetPath("ufw")
                self._ufw_enabled = not "inactive" in self.cuisine.run("ufw status")
        return self._ufw_enabled

    def ufw_enable(self):
        if not self.ufw_enabled:
            if not self.cuisine.isMac:
                if self.executor.type != 'local':
                    self.cuisine.run("ufw allow %s" % self.executor.port)
                self.cuisine.run("echo \"y\" | ufw enable")
                self._ufw_enabled = True
        return True

    @property
    def ufw_rules_allow(self):
        if self.cuisine.isMac:
            return {}
        if self._ufw_allow == {}:
            self._ufw_status()
        return self._ufw_allow

    @property
    def ufw_rules_deny(self):
        if self.cuisine.isMac:
            return {}
        if self._ufw_deny == {}:
            self._ufw_status()
        return self._ufw_deny

    def _ufw_status(self):
        self.ufw_enable()
        out = self.cuisine.run("ufw status", action=True, force=True)
        for line in out.splitlines():
            if line.find("(v6)") != -1:
                continue
            if line.find("ALLOW ") != -1:
                ip = line.split(" ", 1)[0]
                self._ufw_allow[ip] = "*"
            if line.find("DENY ") != -1:
                ip = line.split(" ", 1)[0]
                self._ufw_deny[ip] = "*"

    def allowIncoming(self, port, protocol='tcp'):
        if self.cuisine.isMac:
            return
        self.ufw_enable()
        self.cuisine.run("ufw allow %s/%s" % (port, protocol))

    def denyIncoming(self, port):
        if self.cuisine.isMac:
            return

        self.ufw_enable()
        self.cuisine.run("ufw deny %s" % port)

    def flush(self):
        C = """
        iptables --flush
        iptables --delete-chain
        iptables --table nat --flush
        iptables --table filter --flush
        iptables --table nat --delete-chain
        iptables --table filter --delete-chain
        """
        self.cuisine.run_script(C)

    def show(self):
        print(self.cuisine.run("iptables -t nat -nvL"))
