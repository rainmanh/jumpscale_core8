import re
from JumpScale import j


class NetworkScanner(object):
    COMMAND = 'nmap -n --disable-arp-ping -send-ip -Pn -sS -p{port} -oG - {cidr}'

    def __init__(self, cidr, port=80):
        code, _ = j.sal.process.execute('which nmap', outputToStdout=False, die=False)
        if code != 0:
            raise j.exceptions.RuntimeError('nmap is not installed')

        self._port = port
        self._cidr = cidr

    def scan(self):
        """nmap -n --disable-arp-ping -send-ip -Pn -sS -p22 -oG - 172.17.0.1/24"""

        cmd = self.COMMAND.format(port=self._port, cidr=self._cidr)
        code, output = j.sal.process.execute(cmd, outputToStdout=False, die=False)
        if code != 0:
            raise j.exceptions.RuntimeError('nmap scan failed')

        regex = re.compile(r'^Host: ([^\(]+) .+Ports: %d/open' % self._port, re.MULTILINE)
        hosts = []
        for match in regex.finditer(output):
            hosts.append(match.group(1))

        return hosts