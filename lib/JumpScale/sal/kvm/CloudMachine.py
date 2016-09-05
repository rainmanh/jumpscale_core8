from JumpScale import j
from Machine import Machine

class CloudMachine(Machine):

    def __init__(self, controller, name, os, disks, nics, memory, cpucount, poolname='vms', uuid=None):
        self.pool = j.sal.kvm.Pool(controller, poolname)
        new_nics = list(map(lambda x: j.sal.kvm.Interface(controller, x,
            j.sal.kvm.Network(controller, x, x, [])), nics))
        new_disks = [j.sal.kvm.Disk(controller, self.pool, "%s-base" % name, disks[0], os)]
        for i, disk in enumerate(disks[1:]):
            new_disks.append(j.sal.kvm.Disk(controller, self.pool, "%s-data-%s" % (name, i), disk))

        super().__init__(controller, name, new_disks, new_nics, memory, cpucount, uuid=uuid)


    def create(self):
        [disk.create() for disk in self.disks if not disk.is_created]
        return super().create() if not self.is_created else True

    def start(self):
        return super().start() if not self.is_started else True
