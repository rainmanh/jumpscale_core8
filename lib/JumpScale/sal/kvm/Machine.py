from xml.etree import ElementTree
from JumpScale import j
import libvirt

class Machine:

    STATES = {
        0: "nostate",
        1: "running",
        2: "blocked",
        3: "paused",
        4: "shutdown",
        5: "shutoff",
        6: "crashed",
        7: "pmsuspended",
        8: "last"
    }

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
        machinexml = self.controller.get_template('machine.xml').render({'machinename': self.name, 'memory': self.memory, 'nrcpu': self.cpucount,
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
        try:
            self.domain
            return True
        except libvirt.libvirtError as e:
            return False

    @property
    def is_started(self):
        return bool(self.domain.isActive())

    @property
    def state(self):
        return self.STATES[self.domain.state()[0]]

    def delete(self):
        return self.domain.destroy() == 0

    def pause(self):
        return self.domain.suspend() == 0

    def start(self):
        return self.domain.create() == 0

    def shutdown(self):
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
