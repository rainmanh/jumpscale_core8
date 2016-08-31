from JumpScale import j
from xml.etree import ElementTree as Et 
from jinja2 import Environment, PackageLoader, FileSystemLoader


class Network:

    def __init__(self, controller, name, bridge,  interfaces):
        self.name = name
        self.bridge = bridge
        self.interfaces = interfaces
        self.controller = controller

    def create(self, autostart=True, start=True):
        '''
        @param autostart true will autostart Network on host boot
        create and start network
        '''
        nics = [interface.name for interface in self.interfaces]
        j.sal.openvswitch.newBridge(self.name, nics)
        self.controller.connection.networkDefineXML(self.to_xml())
        nw = self.controller.connection.networkLookupByName(networkname)
        if autostart:
            nw.setAutostart(1)
        if start:
            nw.create()

    def to_xml(self):
        networkxml = self.controller.env.get_template(
            'network.xml').render(networkname=self.name, bridge=self.bridge)
        return networkxml

    def from_xml(self, source):
        network = Et.fromstring(source)
        self.name = network.findtext('name')
        self.bridge = netwrok.findall('bridge')[0].get('name')


    def destroy(self):
        j.sal.openvswitch.netcl.destroyBridge(self.name)


class Interface:

    def __init__(self, controller, name, bridge, interface_rate=None, source=None):

        def generate_mac():
            mac = [0x00, 0x16, 0x3e,
                   random.randint(0x00, 0x7f),
                   random.randint(0x00, 0xff),
                   random.randint(0x00, 0xff)]
            return ':'.join(map(lambda x: '%02x' % x, mac))
        
        if interface_rate:
            self._qos=True
        self.controller = controller
        self.name = name
        self.bridge = bridge
        self.interface_rate = interface_rate
        self._burst = interface_rate*0.1
        self._source = source
        self.mac = generate_mac()

    def from_xml(self, source):
        interface =  Et.fromstring(source)
        self.name = interface.findall('paramaters')[0].get('profileid')
        self.bridge = interface.findall('source')[0].get('bridge')
        bandwidth = interface.findall('bandwidth')
        if bandwidth:
            self.interface_rate = bandwidth[0].find('inbound').get('average')
            self._burst =  bandwidth[0].find('inbound').get('burst')
        self.mac = interface.findall('mac')[0].get('address')

    def to_xml(self):
        Interfacexml = self.controller.env.get_template('interface.xml').render(
            macaddress=self.mac, bridge=self.bridge.name, qos=self.qos, rate=self.interface_rate, burst name=self.name
        )
        return networkxml
