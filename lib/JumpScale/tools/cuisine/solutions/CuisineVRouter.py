
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
        self._cuisine.tmux.executeInScreen('ovsrouter', 'dns', cmd)

    def accesspointAllInOne(self, passphrase, name="", dns="8.8.8.8", interface="wlan0"):
        """
        create an accesspoint with 1 script, do not use if you are using our smarter mitmproxy
        """

        # create_ap --no-virt -m bridge wlan1 eth0 kds10 kds007kds
        # sysctl -w net.ipv4.ip_forward=1
        # iptables -t nat -I POSTROUTING -o wlan0 -j MASQUERADE

        # cmd1='dnsmasq -d'
        if name != "":
            hostname = name
        else:
            _, hostname, _ = self._cuisine.core.run("hostname")
        #--dhcp-dns 192.168.0.149
        _, cpath, _ = self._cuisine.core.run("which create_ap")
        cmd2 = '%s %s eth0 gig_%s %s -d' % (cpath, interface, hostname, passphrase)

        giturl = "https://github.com/oblique/create_ap"
        self._cuisine.pullGitRepo(url=giturl, dest=None, login=None, passwd=None, depth=1,
                                  ignorelocalchanges=True, reset=True, branch=None, revision=None, ssh=False)

        self._cuisine.core.run("cp /opt/code/create_ap/create_ap /usr/local/bin/")

        START1 = """
        [Unit]
        Description = Create AP Service
        Wants = network - online.target
        After = network - online.target

        [Service]
        Type = simple
        ExecStart =$cmd
        KillSignal = SIGINT
        Restart = always
        RestartSec = 5

        [Install]
        WantedBy = multi - user.target
        """
        pm = self._cuisine.processmanager.get("systemd")
        pm.ensure("ap", cmd2, descr="accesspoint for local admin", systemdunit=START1)

    def __str__(self):
        return "cuisine.vrouter:%s:%s" % (getattr(self._executor, 'addr', 'local'), getattr(self._executor, 'port', ''))

    __repr__ = __str__
