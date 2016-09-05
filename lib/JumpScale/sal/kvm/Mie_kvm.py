from xml.etree import ElementTree
from jinja2 import Template
from jinja2 import Environment, PackageLoader, FileSystemLoader
import libvirt
import atexit
from JumpScale import j
from vnic import *
from disk import *

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
        name = machine.findtext('name')
        memory = int(machine.findtext('memory'))
        nrcpu = int(machine.findtext('vcpu'))
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

    @property
    def is_created(self):
        return False

    @property
    def is_started(self):
        return False

    def delete(self):
        return self.domain.destroy() == 0

    def pause(self):
        return self.domain.suspend() == 0

    def start(self):
        return self.domain.create() == 0

    def shuldown(self):
        return self.domain.shutdown() == 0

    def suspend(self):
        return self.domain.suspend() == 0

    def resume(self):
        return self.domain.resume() == 0

    def create_snapshot(self, name, description=""):
        snap = MachineSnapshot(self.controller, self.domain, name, description)
        return snap.create()

    def load_snapshot(self, name):
        snap = self.domain.snapshotLookupByName(name)
        return self.domain.revertToSnapshot(snap)

    def list_snapshots(self, libvirt=False):
        snapshots = []
        snaps = self.domain.listAllSnapshots()
        if libvirt:
            return snaps
        for snap in snaps:
            snapshots.append(MachineSnapshot(
                self.controller, self, snap.getName())
            )
        return snapshots



class MachineSnapshot:

    def __init__(self, controller, domain, name, description=""):
        self.controller = controller
        self.domain = domain
        self.name = name
        self.description = description

    @classmethod
    def from_xml(cls, controller, source):
        snapshot = ElementTree.fromstring(source)
        description = snapshot.findtext('description')
        name = snapshot.findtext('name')
        domain_uuid = snapshot.findall("domain")[0].findtext('uuid')
        domain = controller.connection.lookupByUUIDString(domain_uuid)
        return MachineSnapshot(controller, domain, name, description)

    def to_xml(self):
        snapxml = self.controller.env.get_template(
            'snapshot.xml').render(description=self.description, name=self.name)
        return snapxml

    def create(self):
        snapxml = self.to_xml()
        xml = self.domain.snapshotCreateXML(snapxml)
        return xml


class MachineHelper:

    def create(self, machine):
        [disk.create() for disk in machine.disks]
        [nic.create() for nic in machine.nics]
        return machine.create()

    def start(self, machine):
        pass


class KVMController:

    def __init__(self, host='localhost', executor=None):
        self.executor = executor
        self._host = host
        self.open()
        atexit.register(self.close)
        if executor is None:
            self.executor = j.tools.executor.getLocal()
        self.template_path = j.sal.fs.joinPaths(
            j.sal.fs.getParent(__file__), 'templates')
        self.base_path = "/tmp/base"
        self.env = Environment(loader=FileSystemLoader(self.template_path))
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

    def list_machines(self):
        machines = list()
        domains = self.connection.listAllDomains()
        for domain in domains:
            machine = Machine.from_xml(self, domain.XMLDesc())
            machines.append(machine)
        return machines


class MIE_kvm:

    def __init__(self):
        self.__jslocation__ = "j.sal.our_kvm"
        self.Machine = Machine
        self.KVMController = KVMController
        self.Network = Network
        self.Interface = Interface
        self.Disk = Disk
        self.Pool = Pool
        self.StorageController = StorageController
        self.CloudMachine = CloudMachine

class CloudMachine(Machine):

    POOL = 'vms'

    def __init__(self, controller, name, os, disks, nics, memory, cpucount, uuid=None):
        self.pool = j.sal.our_kvm.Pool(controller, self.POOL)
        new_nics = list(map(lambda x: j.sal.our_kvm.Interface(controller, x,
            j.sal.our_kvm.Network(controller, x, x, [])), nics))
        new_disks = [j.sal.our_kvm.Disk(controller, self.pool, name, 'base', disks[0], os)]
        for i, disk in enumerate(disks[1:]):
            new_disks.append(j.sal.our_kvm.Disk(controller, self.pool, name, 'data-%s'%(i), disk))

        super().__init__(controller, name, new_disks, new_nics, memory, cpucount, uuid=uuid)


    def create(self):
        [disk.create() for disk in self.disks if not disk.is_created]
        [nic.create() for nic in self.nics if not nic.is_created]
        return super().create() if not self.is_created else True

    def start(self):
        [disk.start() for disk in self.disks if not disk.is_started]
        [nic.start() for nic in self.nics if not nic.is_started]
        return super().start() if not self.is_started else True

    def stop(self):
        return self.stop()

    def destroy(self):
        return self.destroy()
