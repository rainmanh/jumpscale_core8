from JumpScale import j
from xml.etree import ElementTree
from jinja2 import Environment, PackageLoader, FileSystemLoader


class Network:
    def __init__(self, controller, name, interfaces):
        self.name = name
        self.interfaces = interfaces
        self.controller = controller

    def create(self, stp=True):
        nics = [interface.name for interface in self.interfaces]
        j.sal.openvswitch.newBridge(self.name, nics)
        self.controller.connection.networkDefineXML(self.to_xml())

    def to_xml(self):
        networkxml = self.controller.env.get_template('network.xml').render(networkname=self.name, bridge=self.name)
        return networkxml

    def destroy(self):
        j.sal.openvswitch.netcl.destroyBridge(self.name)


class Interface:
    def __init__(self, controller, name, bridge):
        self.controller = controller
        self.name = name
        self.bridge = bridge

    def create(self, source):
        j.sal.openvswitch.netcl.connectIfToBridge(self.bridge, self.interface)
        return self.to_xml()

    def to_xml(self):
        Interfacexml = self.controller.env.get_template('interface.xml').render(bridge=self.bridge.name, name=self.name)
        return networkxml
    