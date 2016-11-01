
from JumpScale import j

# import inspect


class ZeroNetConfig():

    def __init__(self):
        self.__jslocation__ = "j.sal.zeronetconfig"
        self.logger = j.logger.get("j.sal.zeronetconfig")

    def get(self, addr):
        """
        @param addr is e.g. myserver or myserver:2022
        """
        return ZeroNetConfigHost(addr)


class ZeroNetConfigHost():

    def __init__(self, addr):
        self._cuisine = j.tools.cuisine.get(addr)

        # self.db = j.clients.redis.get("localhost", 3629)
        self.db = j.core.db
        self.example()

        # self._path = j.sal.fs.getDirName(inspect.getfile(self.__init__))
        #
        # c = j.sal.fs.fileGetContents(j.sal.fs.joinPaths(self._path, "dnsFilter.lua"))
        #
        # self.checkdns = self.db.register_script(c)

    def install(self):
        pass

    def example(self):

        # ERASE
        for key in self.db.keys():
            key = key.decode()
            if key.startswith("netconfig"):
                self.db.delete(key)

        # DNS config
        self.db.hset("netconfig:dns:config:mydomain.com:a", "www.", "192.168.1.1")
        self.db.hset("netconfig:dns:config:mydomain.com:a", "www3", "192.168.1.1,192.168.1.2")
        self.db.hset("netconfig:dns:config:mydomain.com:mx", "", "mail.mydomain.com,mail2.mydomain.com")
        self.db.hset("netconfig:dns:config:mydomain.com:alias", "www2", "www.mydomain.com")

        # DNS filter
        endswithFilter = ["microsoft.com", "apple.com"]
        self.db.set("netconfig:dns:filter:endswithfilter", j.data.serializer.json.dumps(endswithFilter))
        regexfilter = [".*update.*", ".*download.*", ".*\.py"]
        self.db.set("netconfig:dns:filter:regexfilter", j.data.serializer.json.dumps(regexfilter))

        # DHCP config
        self.db.hset("netconfig:dhcp:config:fixed", "38:c9:86:20:64:37", "192.168.10.1")
        self.db.hset("netconfig:dhcp:config:range", "eth0", "192.168.10.0/24")
