from JumpScale import j
import netifaces

from sal.base.SALObject import SALObject


class DHCP():
    def __init__(self):
        self.__jslocation__="j.sal.dhcp_ihc"
        self.configPath = j.tools.path.get('/etc').joinpath('dhcp3', 'dhcpd.conf')
        self._executor = j.tools.executor.getLocal()

    def configure(self, ipFrom, ipTo, interface):
        interface = netifaces.ifaddresses(interface)[2]
        if self.configPath.exists():
            header = '''default-lease-time 600;
max-lease-time 7200;
'''
            self.configPath.touch()
            self.configPath.write_text(header)

        config = '''
subnet %s netmask %s {
    option subnet-mask 255.255.255.0;
    option routers 10.0.0.1;
    range %s %s;
}''' % (interface['addr'], interface['netmask'], ipFrom, ipTo)

        self.configPath.write_text(config, append=True)
        self.restart()

    def start(self):
        self._executor.execute('service isc-dhcp-server start')

    def stop(self):
        self._executor.execute('service isc-dhcp-server stop')

    def restart(self):
        self._executor.execute('service isc-dhcp-server restart')
