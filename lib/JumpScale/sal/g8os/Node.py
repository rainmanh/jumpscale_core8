from JumpScale import j
from JumpScale.sal.g8os.Disk import Disk
from JumpScale.sal.g8os.Disk import DiskType


class Node:
    """Represent a G8OS Server"""

    def __init__(self, addr, port=6379, password=None):
        # g8os client to talk to the node
        self._client = j.clients.g8core.get(host=addr, port=port, password=password)
        self.addr = addr
        self.port = port
        self.disks = []

        self._load()

    def _load(self):
        """
        load the attribute of this node from the client
        """
        for disk_info in self._client.disk.list()['blockdevices']:
            self.disks.append(Disk(
                client=self._client,
                node=self,
                disk_info=disk_info
            ))

    def get_disk(self, name):
        """
        return the disk called `name`
        @param name: name of the disk
        """
        for disk in self.disks:
            if disk.name == name:
                return disk
        return None

    def _eligible_fscache_disk(self):
        """
        return the first disk that is eligible to be used as filesystem cahe
        First try to find a SSH disk, otherwise return a HDD
        """
        # Pick up the first ssd
        for disk in self.disks:
            if disk.type in [DiskType.ssd, DiskType.nvme]:
                return disk
        # If no SSD found, pick up the first disk
        return self.disks[0]

    def _mount_fscache(self, partition):
        """
        mount the fscache partition and copy the content of the in memmory fs inside
        """
        partition.umount()

         # saving /tmp/ contents
        self._client.bash("mkdir -p /tmpbak").get()
        self._client.bash("cp -arv /tmp/* /tmpbak/").get()

        # mount /tmp
        partition.mount('/tmp')

        # restoring /tmp
        self._client.bash("cp -arv /tmpbak/* /tmp/").get()
        self._client.bash("rm -rf /tmpbak").get()


    def ensure_persistance(self):
        """
        look for a disk not used,
        create a partition and mount it to be used as cache for the g8ufs
        set the label `fs_cache` to the partition
        """
        if len(self.disks) <= 0:
            # if no disks, we can't do anything
            return

        # check if there is already a partition with the fs_cache label
        partition = None
        for disk in self.disks:
            for part in disk.partitions:
                for fs in part.filesystems:
                    if fs['label'] == 'fs_cache':
                        partition = part
                        break

        # create the partition if we don't have one yet
        if partition is None:
            disk = self._eligible_fscache_disk()

            disk.mktable(table_type='gpt', overwrite=True)

            if len(disk.partitions) <= 0:
                partition = disk.mkpart(start=disk.blocksize, end='100%')
            else:
                partition = disk.partitions[0]

            if len(partition.filesystems) <= 0:
                self._client.btrfs.create(
                    label='fs_cache',
                    devices=["/dev/{}".format(partition.name)],
                    metadata_profile='single',
                    data_profile='single'
                )

        # mount the partition
        self._mount_fscache(partition)
        return partition


    def __str__(self):
        return "Node <{host}:{port}>".format(
            host=self.addr,
            port=self.port,
        )

    def __repr__(self):
        return str(self)
