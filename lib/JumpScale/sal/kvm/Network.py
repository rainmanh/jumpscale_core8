from xml.etree import ElementTree
from BaseKVMComponent import BaseKVMComponent


class Network(BaseKVMComponent):
    """Network object representation of xml and actual Network."""

    def __init__(self, controller, name, bridge=None, interfaces=[]):
        """
        Instance of network object representation of open vstorage network.

        @param controller object: connection to libvirt controller.
        @param name string: name of network.
        @param bridge string: bridge name.
        @param interfaces list: interfaces list.
        """
        self.name = name
        self.bridge = bridge if bridge else name
        self._interfaces = interfaces
        self.controller = controller

    @property
    def interfaces(self):
        """
        Return list of interfaces names added to the bridge of the current network
        """
        if self._interfaces is None:
            if self.bridge in self.controller.executor.execute("ovs-vsctl list-br"):
                self._interfaces = self.controller.executor.execute(
                    "ovs-vsctl list-ports %s" % self.bridge)
            else:
                return []
        return self._interfaces

    def create(self, start=True, autostart=True):
        '''
        @param start bool: will start the network after creating it
        @param autostart bool: will autostart Network on host boot
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
        """
        Return libvirt's xml string representation of the Network.
        """
        networkxml = self.controller.get_template(
            'network.xml').render(networkname=self.name, bridge=self.bridge)
        return networkxml

    @classmethod
    def from_xml(cls, controller, source):
        """
        Instantiate a Network object using the provided xml source and kvm controller object.

        @param controller object(j.sal.kvm.KVMController): controller object to use.
        @param source  str: xml string of machine to be created.
        """
        network = ElementTree.fromstring(source)
        name = network.findtext('name')
        bridge = network.findall('bridge')[0].get('name')
        return cls(controller, name, bridge, None)

    def destroy(self):
        """
        Destroy network.
        """
        self.controller.executor.execute(
            'ovs-vsctl --if-exists del-br %s' % self.name)
