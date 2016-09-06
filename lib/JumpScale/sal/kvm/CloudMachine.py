from JumpScale import j
from Machine import Machine

class CloudMachine(Machine):

    def __init__(self, controller, name, os, disks, nics, memory, cpucount, poolname='vms', uuid=None):
        self.pool = j.sal.kvm.Pool(controller, poolname)
        self.os = os
        new_nics = list(map(lambda x: j.sal.kvm.Interface(controller, x,
            j.sal.kvm.Network(controller, x, x, [])), nics))
        if disks:
            new_disks = [j.sal.kvm.Disk(controller, self.pool, "%s-base" % name, disks[0], os)]
            for i, disk in enumerate(disks[1:]):
                new_disks.append(j.sal.kvm.Disk(controller, self.pool, "%s-data-%s" % (name, i), disk))
        else:
            new_disks = []

        super().__init__(controller, name, new_disks, new_nics, memory, cpucount, uuid=uuid)

    @classmethod
    def from_xml(cls, controller, xml):
        m = Machine.from_xml(controller, xml)
        return cls(m.controller, m.name, m.disks and m.disks[0].image_name,
            list(map(lambda disk:disk.size, m.disks)), list(map(lambda nic:nic.name, m.nics)),
            m.memory, m.cpucount, m.disks and m.disks[0].pool.name)

    def create(self):
        [disk.create() for disk in self.disks if not disk.is_created]
        return super().create() if not self.is_created else False

    def start(self):
        return super().start() if not self.is_started else False

    def delete(self):
        return super().delete() if self.is_created else False

    def shutdown(self):
        return super().shutdown() if self.is_started else False

    stop = shutdown

    def suspend(self):
        return super().suspend() if self.is_started else False

    pause = suspend

    def resume(self):
        return super().resume() if self.state == "paused" else False
