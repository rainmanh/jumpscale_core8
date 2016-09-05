from JumpScale import j
from xml.etree import ElementTree
import random


class Network:
    """Network object representation of xml and actual Network."""

    def __init__(self, controller, name, bridge=None, interfaces=[]):
        """
        Instance of network object representation of open vstorage network.

        @param controller object: connection to libvirt controller
        @param name string: name of network
        @param bridge
        @param interfaces
        """
        self.name = name
        self.bridge = bridge if bridge else name
        self._interfaces = interfaces
        self.controller = controller

    @property
    def interfaces(self):
        if self._interfaces is None:
            if self.bridge in self.controller.executor.execute("ovs-vsctl list-br"):
                self._interfaces = self.controller.executor.execute(
                    "ovs-vsctl list-ports %s" % self.bridge)
            else:
                return []
        return self._interfaces

    def create(self, autostart=True, start=True):
        '''
        @param autostart true will autostart Network on host boot
        create and start network
        '''
        nics = [interface for interface in self.interfaces]

        self.controller.executor.execute(
            "ovs-vsctl --may-exist add-br %s" % self.name)
        self.controller.executor.execute(
            "ovs-vsctl set Bridge %s stp_enable=true" % self.name)
        if nics:
            for nic in nics:
                self.controller.executor.execute(
                    "ovs-vsctl --may-exist add-port %s %s" % (self.name, nic))

        self.controller.connection.networkDefineXML(self.to_xml())
        nw = self.controller.connection.networkLookupByName(self.name)
        if autostart:
            nw.setAutostart(1)
        if start:
            nw.create()

    def to_xml(self):
        networkxml = self.controller.env.get_template(
            'network.xml').render(networkname=self.name, bridge=self.bridge)
        return networkxml

    @classmethod
    def from_xml(cls, controller, source):
        network = ElementTree.fromstring(source)
        name = network.findtext('name')
        bridge = network.findall('bridge')[0].get('name')
        return cls(controller, name, bridge, None)

    def destroy(self):
        self.controller.executor.execute(
            'ovs-vsctl --if-exists del-br %s' % self.name)


class Interface:

    def __init__(self, controller, name, bridge, interface_rate=None, source=None):

        def generate_mac():
            mac = [0x00, 0x16, 0x3e,
                   random.randint(0x00, 0x7f),
                   random.randint(0x00, 0xff),
                   random.randint(0x00, 0xff)]
            return ':'.join(map(lambda x: '%02x' % x, mac))

        self.controller = controller
        self.name = name
        self.bridge = bridge
        self.qos = not (interface_rate is None)
        self.interface_rate = str(interface_rate)
        self.burst = None
        if not (interface_rate is None):
            self.burst = str(int(interface_rate * 0.1))
        self._source = source
        self.mac = generate_mac()

    def destroy(self):
        """
        Delete interface and port related to certain machine.

        @bridge str: name of bridge
        @name str: name of port and interface to be deleted
        """
        return self.controller.executor.execute('ovs-vsctl del-port %s %s' % (self.bridge.name, self.name))

    def qos(self, qos, burst=None):
        """
        Limit the throughtput into an interface as a for of qos.

        @interface str: name of interface to limit rate on
        @qos int: rate to be limited to in Kb
        @burst int: maximum allowed burst that can be reached in Kb/s
        """
        # TODO: *1 spec what is relevant for a vnic from QOS perspective, what can we do
        # goal is we can do this at runtime
        self.controller.executor.execute(
            'ovs-vsctl set interface %s ingress_policing_rate=%d' % (self.name, qos))
        if not burst:
            burst = int(qos * 0.1)
        self.controller.executor.execute(
            'ovs-vsctl set interface %s ingress_policing_burst=%d' % (self.name, burst))

    def from_xml(self, source):
        interface = ElementTree.fromstring(source)
        self.name = interface.findall('paramaters')[0].get('profileid')
        self.bridge = interface.findall('source')[0].get('bridge')
        bandwidth = interface.findall('bandwidth')
        if bandwidth:
            self.interface_rate = bandwidth[0].find('inbound').get('average')
            self.burst = bandwidth[0].find('inbound').get('burst')
        self.mac = interface.findall('mac')[0].get('address')

    def to_xml(self):
        Interfacexml = self.controller.env.get_template('interface.xml').render(
            macaddress=self.mac, bridge=self.bridge.name, qos=self.qos, rate=self.interface_rate, burst=self.burst, name=self.name
        )
        return Interfacexml
