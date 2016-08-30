from JumpScale import j
from xml.etree import ElementTree
from jinja2 import Environment, PackageLoader, FileSystemLoade


class Network:
    def __init__(self, name, interfaces):
        self.name = name
        self.interfaces = interfaces
        self.env = Environment(loader=FileSystemLoader(
            j.sal.fs.joinPaths(j.sal.fs.getParent(__file__), 'templates')))

    def create(self, stp=True, ):
        nics = [interface.name for interface in self.interfaces]
        j.sal.openvswitch.newBridge(self.name, nics)
        network_xml = self.env.get_template('network.xml').render(
            bridge=self.name, networkname=self.name
        )

    def toXml(self):
        pass

    def destroy(self):
        j.sal.openvswitch.netcl.destroyBridge(self.name)


class Interface:
    def __init__(self, name):
        self.name = name

    def create(self):
        pass

    def toXml(self):
        pass