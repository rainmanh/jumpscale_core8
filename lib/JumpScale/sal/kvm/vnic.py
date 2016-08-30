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
        networkxml = self.controller.env.get_template('network.xml').render({'networkname': self.name, 'bridge': self.name})
        return networkxml

    def destroy(self):
        j.sal.openvswitch.netcl.destroyBridge(self.name)


class Interface:
    def __init__(self, name):
        self.name = name

    def create(self):
        pass

    def to_xml(self):
        pass