from xml.etree import ElementTree
from JumpScale import j
import libvirt
import yaml
from BaseKVMComponent import BaseKVMComponent
import re

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
        self.image_path = "%s/%s_ci.iso" % (self.controller.base_path, self.name) if cloud_init else ""
        self._domain = None
        self._ip = None
        self._executor = None

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
        xml_disks = [disk for disk in machine.find('devices').findall('disk') if disk.get('device') == 'disk']
        disks = list(map(lambda disk:j.sal.kvm.Disk.from_xml(controller, ElementTree.tostring(disk)),
            xml_disks))
        cloud_init = bool([disk for disk in machine.find('devices').findall('disk') if disk.get('device') == 'cdrom'])
        return cls(controller, name, disks, interfaces, memory, nrcpu, cloud_init=cloud_init)

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
    @property
    def ip(self):
        """
        return the ip of the machine
        """

        if not self._ip:
            for nic in self.nics:
                import pudb; pu.db
                bridge_name = nic.bridge.name
                mac = nic.mac
                rc, ip, err = self.controller.executor.execute("nmap -sn $(ip r | grep %s | grep -v default | awk '{print $1}') | grep -iB 2 '%s' | head -n 1 | awk '{print $NF}'" % (bridge_name, mac))
                ip_pat = re.compile("\d{1,3}.\d{1,3}.\d{1,3}.\d{1,3}")
                m = ip_pat.search(ip)
                if m:
                    self._ip = m.group()
                if self._ip:
                    break
        return self._ip

    @property
    def executor(self):
        if self.cloud_init and not self._executor:
            self.controller.executor.getSSHViaProxy(self.controller.executor.addr,
                getattr(self.controller.executor.cuisine, 'login', 'root'), m.ip, "cloudscalers", 22, "/root/.ssh/libvirt")
        return self._executor

    @property
    def cuisine(self):
        return self.executor.cuisine

    def create(self, username="cloudscalers", passwd="gig1234"):
        cuisine = self.controller.executor.cuisine
        if self.cloud_init:
            cuisine.core.dir_ensure("%s/metadata/%s" % (self.controller.base_path, self.name))
            userdata = "#cloud-config\n"
            userdata += yaml.dump({'chpasswd': {'expire': False},
                                   'ssh_pwauth': True,
                                   'users': [{'lock-passwd': False,
                                              'name': 'cloudscalers',
                                              'plain_text_passwd': 'gig1234',
                                              'shell': '/bin/bash',
                                              'ssh-authorized-keys': ['pubkey'],
                                              'sudo': 'ALL=(ALL) ALL'}]
                                  })
            metadata = '{"local-hostname":"vm-%s"}' % self.name
            cuisine.core.file_write("%s/metadata/%s/user-data" % (self.controller.base_path, self.name), userdata)
            cuisine.core.file_write("%s/metadata/%s/meta-data" % (self.controller.base_path, self.name), metadata)
            cmd = "genisoimage -o {base}/{name}_ci.iso -V cidata -r -J {base}/metadata/{name}/meta-data {base}/metadata/{name}/user-data".format(base=self.controller.base_path, name=self.name)
            cuisine.core.run(cmd)
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
