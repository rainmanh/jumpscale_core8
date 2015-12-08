from JumpScale import j
import signal


DOMAIN = 'network'

from sal.base.SALObject import SALObject

class DNSMasq(SALObject):

    def __init__(self):
        self.__jslocation__ = "j.sal.dnsmasq"
        self._configured = False
        self._executor = j.tools.executor.getLocal()

    def setConfigPath(self, namespace=None, config_path=None):
        if not config_path:
            self._configdir = j.tools.path.get('/etc').joinpath('dnsmasq')
        else:
            self._configdir = j.tools.path.get(config_path)
        if not j.sal.ubuntu.findPackagesInstalled('dnsmasq'):
            j.sal.ubuntu.install('dnsmasq')
        self._hosts = self._configdir.joinpath('hosts')
        self._pidfile = self._configdir.joinpath('dnsmasq.pid')
        self._leasesfile = self._configdir.joinpath('dnsmasq.leases')
        self._configfile = self._configdir.joinpath('dnsmasq.conf')
        #if namespace:
        #    self._namespace = namespace
        #    self._startupmanagername = 'dnsmasq_%s' % (namespace)
        #else: 
        #    self._startupmanagername = 'dnsmasq'
        #startname = '%s__%s' % ('network', self._startupmanagername)
        # @TODO startupmanager deprecated. Should be managed through AYS (*2*)
        #if startname not in j.tools.startupmanager.listProcesses():
        #    self.addToStartupManager()
        self._configured = True

    # @TODO startupmanager deprecated. Should be managed through AYS (*2*)
    #def addToStartupManager(self):
    #    if self._namespace:
    #        cmd = 'ip netns exec %(namespace)s dnsmasq -k --conf-file=%(configfile)s --pid-file=%(pidfile)s --dhcp-hostsfile=%(hosts)s --dhcp-leasefile=%(leases)s' % {'namespace':self._namespace,'configfile':self._configfile, 'pidfile': self._pidfile, 'hosts': self._hosts, 'leases': self._leasesfile}
    #    else:
    #        cmd = 'dnsmasq -k --conf-file=%(configfile)s --pid-file=%(pidfile)s --dhcp-hostsfile=%(hosts)s --dhcp-leasefile=%(leases)s' % {'configfile':self._configfile, 'pidfile': self._pidfile, 'hosts': self._hosts, 'leases': self._leasesfile}
    #    j.tools.startupmanager.addProcess(self._startupmanagername, cmd, reload_signal=signal.SIGHUP, domain=DOMAIN)
    #    j.tools.startupmanager.startProcess(DOMAIN, self._startupmanagername)

    
    def _checkFile(self, filename):
        filepath = j.tools.path.get(filename)
        if not filepath.exists():
            filepath.touch()
         

    def addHost(self, macaddress, ipaddress, name=None):
        if not self._configured:
            raise Exception('Please run first setConfigPath to select the correct paths')
        """Adds a dhcp-host entry to dnsmasq.conf file"""
        self._checkFile(self._hosts)
        te = j.tools.code.getTextFileEditor(self._hosts)
        contents = '%s' % macaddress
        if name:
            contents += ',%s' % name
        contents += ',%s\n' % ipaddress
        te.appendReplaceLine('.*%s.*' % macaddress, contents)
        te.save()
        self.reload()

    def removeHost(self, macaddress):
        """Removes a dhcp-host entry from dnsmasq.conf file"""
        if not self._configured:
            raise Exception('Please run first setConfigPath to select the correct paths')
        self._checkFile(self._hosts)
        te = j.tools.code.getTextFileEditor(self._hosts)
        te.deleteLines('.*%s.*' % macaddress)
        te.save()
        self.reload()

    def restart(self):
        """Restarts dnsmasq"""
        if not self._configured:
            raise Exception('Please run first setConfigPath to select the correct paths')
        self._executor.execute('service dnsmasq restart')
        # @TODO startupmanager deprecated. Should be managed through AYS (*2*)
        #j.tools.startupmanager.load()
        #j.tools.startupmanager.restartProcess(DOMAIN, self._startupmanagername)

    def reload(self):
        if not self._configured:
            raise Exception("Please run first setConfigPath to select the correct paths")
        self._executor.execute('service dnsmasq reload')
        # @TODO startupmanager deprecated. Should be managed through AYS (*2*)
        j.tools.startupmanager.load()
        j.tools.startupmanager.reloadProcess(DOMAIN, self._startupmanagername)
