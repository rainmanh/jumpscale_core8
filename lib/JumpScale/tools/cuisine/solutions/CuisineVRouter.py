
from JumpScale import j
import os
import time

import socket


base = j.tools.cuisine._getBaseClass()


class CuisineVRouter(base):
    """
    """

    def __init__(self, executor, cuisine):
        self._executor = executor
        self._cuisine = cuisine
        self.cuisine = self._cuisine
        self._defgwInterface = None

    @property
    def defgwInterface(self):
        if self._defgwInterface == None:
            self._defgwInterface = self.cuisine.net.defaultgwInterface
        return self._defgwInterface

    def runsolution(self):
        self.prepare()
        self.dnsServer()

    def prepare(self):
        # will make sure jumpscale has been installed (&base)
        c.development.js8.install()
        j.do.pullGitRepo("git@github.com:despiegk/smartproxy.git")
        self._cuisine.core.upload("$codeDir/github/jumpscale/smartproxy")
        C = """
        ln -s $codeDir/github/jumpscale/smartproxy /opt/dnsmasq-alt
        """
        self.cuisine.core.execute_bash(C)

    def dnsServer(self):
        # TODO: *1 something wrong in next line, it doesn't create session, need to create if it doesn't exist otherwise no
        # self._cuisine.tmux.createSession("ovsrouter",["dns"])
        self._cuisine.process.kill("dns-server")
        cmd = "jspython /opt/dnsmasq-alt/dns-server.py"
        self.cuisine.tmux.executeInScreen('ovsrouter', 'dns', cmd)

    @property
    def wirelessInterfaceNonDefGW(self):
        """
        find wireless interface which is not the def gw
        needs to be 1
        """
        interfaces = [item for item in self.cuisine.net.wirelessLanInterfaces if item != self.defgwInterface]
        if len(interfaces) != 1:
            raise j.exceptions.Input(
                message="Can only create access point if 1 wireless interface found which is not the default gw.", level=1, source="", tags="", msgpub="")
        return interfaces[0]

    @property
    def freeNetworkRangeDMZ(self):
        """
        look for free network range
        default: 192.168.100.0/24
        and will go to 101... when not available
        """
        for i in range(100, 150):
            iprange = "192.168.%s" % i
            for item in self.cuisine.net.ips:
                if not item.startswith(iprange):
                    return iprange
        raise j.exceptions.Input(message="Cannot find free dmz iprange", level=1, source="", tags="", msgpub="")

    def dhcpServer(self, interfaces=[]):
        """
        will run dhctp server in tmux on interfaces specified
        if not specified then will look for wireless interface which is used in accesspoint and use that one
        """
        self.cuisine.package.install("isc-dhcp-server")
        if interfaces == []:
            interfaces = [self.wirelessInterfaceNonDefGW]
        r = self.freeNetworkRangeDMZ
        config = """
        subnet $range.0 netmask 255.255.255.0 {
          range $range.100 $range.200;
          option domain-name-servers $range.254;
          option subnet-mask 255.255.255.0;
          option routers $range.254;
          option broadcast-address $range.255;
          default-lease-time 600;
          max-lease-time 7200;
        }
        """
        config = config.replace("$range", r)
        self.cuisine.core.file_write("/etc/dhcp/dhcpd.conf", config)

        from IPython import embed
        print("DEBUG NOW dhcp")
        embed()
        raise RuntimeError("stop debug here")
        self._cuisine.process.kill("dns-server")
        cmd = "jspython /opt/dnsmasq-alt/dns-server.py"
        self._cuisine.tmux.executeInScreen('ovsrouter', 'dns', cmd)

    def wirelessAccesspoint(self, sid="myap", passwd="12345678"):
        """
        will look for free wireless interface which is not the def gw
        this interface will be used to create an accesspoint
        """
        self.wirelessInterfaceNonDefGW
        from IPython import embed
        print("DEBUG NOW ")
        embed()
        raise RuntimeError("stop debug here")

    #
    # def accesspointAllInOne(self, passphrase, name="", dns="8.8.8.8", interface="wlan0"):
    #     """
    #     create an accesspoint with 1 script, do not use if you are using our smarter mitmproxy
    #     """
    #
    #     # create_ap --no-virt -m bridge wlan1 eth0 kds10 kds007kds
    #     # sysctl -w net.ipv4.ip_forward=1
    #     # iptables -t nat -I POSTROUTING -o wlan0 -j MASQUERADE
    #
    #     # cmd1='dnsmasq -d'
    #     if name != "":
    #         hostname = name
    #     else:
    #         _, hostname, _ = self._cuisine.core.run("hostname")
    #     #--dhcp-dns 192.168.0.149
    #     _, cpath, _ = self._cuisine.core.run("which create_ap")
    #     cmd2 = '%s %s eth0 gig_%s %s -d' % (cpath, interface, hostname, passphrase)
    #
    #     giturl = "https://github.com/oblique/create_ap"
    #     self._cuisine.pullGitRepo(url=giturl, dest=None, login=None, passwd=None, depth=1,
    #                               ignorelocalchanges=True, reset=True, branch=None, revision=None, ssh=False)
    #
    #     self._cuisine.core.run("cp /opt/code/create_ap/create_ap /usr/local/bin/")
    #
    #     START1 = """
    #     [Unit]
    #     Description = Create AP Service
    #     Wants = network - online.target
    #     After = network - online.target
    #
    #     [Service]
    #     Type = simple
    #     ExecStart =$cmd
    #     KillSignal = SIGINT
    #     Restart = always
    #     RestartSec = 5
    #
    #     [Install]
    #     WantedBy = multi - user.target
    #     """
    #     pm = self._cuisine.processmanager.get("systemd")
    #     pm.ensure("ap", cmd2, descr="accesspoint for local admin", systemdunit=START1)

    def __str__(self):
        return "cuisine.vrouter:%s:%s" % (getattr(self._executor, 'addr', 'local'), getattr(self._executor, 'port', ''))

    __repr__ = __str__
