from xml.etree import ElementTree
from JumpScale import j
import libvirt
import yaml
from BaseKVMComponent import BaseKVMComponent

class Machine(BaseKVMComponent):

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

    def __init__(self, controller, name, disks, nics, memory, cpucount, uuid=None, cloud_init=False):
        self.name = name
        self.disks = disks
        self.nics = nics
        self.memory = memory
        self.cpucount = cpucount
        self.controller = controller
        self._uuid = uuid
        self.cloud_init = cloud_init
        self.image_path=""
        self._domain = None

    def to_xml(self):
        machinexml = self.controller.get_template('machine.xml').render({'machinename': self.name, 'memory': self.memory, 'nrcpu': self.cpucount,
                                                                             'nics': self.nics, 'disks': self.disks, "cloudinit": self.cloud_init, 
                                                                             "image_path":self.image_path})
        return machinexml

    @classmethod
    def from_xml(cls, controller, source):
        machine =  ElementTree.fromstring(source)
        name = machine.findtext('name')
        memory = int(machine.findtext('memory'))
        nrcpu = int(machine.findtext('vcpu'))
        interfaces = list(map(lambda interface:j.sal.kvm.Interface.from_xml(controller, ElementTree.tostring(interface)),
            machine.find('devices').findall('interface')))
        disks = list(map(lambda disk:j.sal.kvm.Disk.from_xml(controller, ElementTree.tostring(disk)),
            machine.find('devices').findall('disk')))
        return cls(controller, name, disks, interfaces, memory, nrcpu)

    @classmethod
    def get_by_name(cls, controller, name):
        domain = controller.connection.lookupByName(name)
        return cls.from_xml(controller, domain.XMLDesc())

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

#     def forward_host(self, vmport):
#         cmd = "ssh -L {hostport}:{vmip}:{vmport} -p 9022".format(hostport=, vmip=, vmport=)
#         self._connection.cuisine.execute(cmd)
#         executor = j.tools.executor.getSSHBased(pubkey=)
#         vmcuisine = executor.cuisine
#         return vmcuisine
#
#     def proxyintovm(self):
#         sshconfig = """
# Host {host}
# HostName {hostname}
# User {user}
# ProxyCommand ssh {user}@{physicalhost} nc %h %p
#         """.format(host=host, hostname=hostname, user=user, physicalhost=physicalhost)
#         #write that in the host
#         self.controller.cuisine.file_write("/root/.ssh/sshconfig", append=True)
#
#         #now get the cuisine of the virtual vm

    def create(self, username="cloudscalers", passwd="gig1234"):
        cuisine = self.controller.executor.cuisine
        if self.cloud_init:
            cuisine.core.dir_ensure("%s/metadata/%s" % (self.controller.base_path, self.name))
            userdata = self.controller.get_template('user-data.yaml').render(pubkey=self.controller.pubkey)
            metadata = '{"local-hostname":"vm-%s"}' % self.name
            cuisine.core.file_write("%s/metadata/%s/user-data" % (self.controller.base_path, self.name), userdata)
            cuisine.core.file_write("%s/metadata/%s/meta-data" % (self.controller.base_path, self.name), metadata)
            cmd = "genisoimage -o {base}/{name}_ci.iso -V cidata -r -J {base}/metadata/{name}/meta-data {base}/metadata/{name}/user-data".format(base=self.controller.base_path, name=self.name)
            cuisine.core.run(cmd)
            self.image_path = "%s/%s_ci.iso" % (self.controller.base_path, self.name)
            cuisine.core.dir_remove("%s/images/%s " % (self.controller.base_path, self.name))
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
        return self.domain.undefine() == 0

    def start(self):
        return self.domain.create() == 0

    def shutdown(self, force=False):
        if force:
            return self.domain.destroy() == 0
        else:
            return self.domain.shutdown() == 0

    stop = shutdown

    def suspend(self):
        return self.domain.suspend() == 0

    pause = suspend

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
