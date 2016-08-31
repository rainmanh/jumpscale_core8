from xml.etree import ElementTree
from jinja2 import Template
from jinja2 import Environment, PackageLoader, FileSystemLoader
import libvirt
import atexit
from JumpScale import j
from vnic import *

class Machine:

    def __init__(self, controller, name, disks, nics, memory, cpucount, uuid=None):
        self.name = name
        self.disks = disks
        self.nics = nics
        self.memory = memory
        self.cpucount = cpucount
        self.controller = controller
        self._uuid = uuid
        self._domain = None

    def to_xml(self):
        machinexml = self.controller.env.get_template('machine.xml').render({'machinename': self.name, 'memory': self.memory, 'nrcpu': self.cpucount,
            'nics': self.nics, 'disks': self.disks})
        return machinexml

    @classmethod
    def from_xml(cls, controller, source):
        machine =  ElementTree.fromstring(source)
        name = interface.findtext('name')
        memory = int(interface.findtext('memory'))
        nrcpu = int(interface.findtext('vcpu'))
        interfaces = map(lambda interface:Interface.from_xml(controller, ElementTree.tostring(interface)),
            machine.findall('interface'))
        disks = map(lambda disk:Disk.from_xml(controller, ElementTree.tostring(disk)),
            machine.findall('disk'))
        return cls(controller, name, disks, interfaces, memory, nrcpu)

    @property
    def domain(self):
        if not self._domain:
            if self._uuid:
                self._domain = self.controller.connection.lookupByUUIDString(self._uuid)
            else:
                self._domain = self.controller.connection.lookupByName(self.name)
        return self._domain
    
    @domain.setter
    def domain(self, val):
        self._domain = val

    @property
    def uuid(self):
        if not self._uuid:
            self._uuid = self.domain.UUIDString()
        return self._uuid

    def create(self):
        self.domain = self.controller.connection.defineXML(self.to_xml())

    def delete(self):
        return domain.destroy() == 0

    def start(self):
        return self.domain.create() == 0

    def shuldown(self):
        return self.domain.shutdown() == 0

    def suspend(self):
        return self.domain.suspend() == 0

    def resume(self):
        return self.domain.resume() == 0

class MachineHelper:

    def create(self, machine):
        [disk.create() for disk in machine.disks]
        [nic.create() for nic in machine.nics]
        return machine.create()

    def start(self, machine):
        pass


class KVMController:

    def __init__(self, host='localhost'):
        self._host = host
        self.open()
        atexit.register(self.close)
        self.env = Environment(loader=FileSystemLoader(
            j.sal.fs.joinPaths(j.sal.fs.getParent(__file__), 'templates')))
        # self.env = Environment(loader=FileSystemLoader('/'.join(file.split('/')[:-1]) + '/templates'))

    def open(self):
        uri = None
        if self._host != 'localhost':
            uri = 'qemu+ssh://%s/system' % self._host
        self.connection = libvirt.open(uri)
        self.readonly = libvirt.openReadOnly(uri)

    def close(self):
        def close(con):
            if con:
                try:
                    con.close()
                except:
                    pass
        close(self.connection)
        close(self.readonly)

class MIE_kvm:
    def __init__(self):
        self.__jslocation__ = "j.sal.our_kvm"
        self.Machine = Machine
        self.KVMController = KVMController
        self.Network = Network
        self.Interface = Interface

