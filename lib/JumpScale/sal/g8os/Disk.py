from enum import Enum
from JumpScale.sal.g8os.Partition import Partition


class DiskType(Enum):
    ssd = "ssd"
    hdd = "hdd"
    nvme = "nvme"
    archive = "archive"
    cdrom = 'cdrom'


class Disk:
    """Disk in a G8OS"""

    def __init__(self, client, node, disk_info):
        """
        disk_info: dict returned by client.disk.list()
        """
        # g8os client to talk to the node
        self._client = client
        self.node = node
        self.name = None
        self.size = None
        self.blocksize = None
        self.partition_table = None
        self.mountpoint = None
        self.model = None
        self._filesystems = []
        self.type = None
        self.partitions = []

        self._load(disk_info)

    @property
    def filesystems(self):
        self._populate_filesystems()
        return self._filesystems

    def _load(self, disk_info):
        detail = self._client.disk.getinfo(disk_info['name'])
        self.name = disk_info['name']
        self.size = int(disk_info['size'])
        self.blocksize = detail['blocksize']
        if detail['table'] != 'unknown':
            self.partition_table = detail['table']
        self.mountpoint = disk_info['mountpoint']
        self.model = disk_info['model']
        self.type = self._disk_type(disk_info)
        for partition_info in disk_info.get('children', []):

            self.partitions.append(
                Partition(
                    client=self._client,
                    disk=self,
                    part_info=partition_info)
            )

    def _populate_filesystems(self):
        """
        look into all the btrfs filesystem and populate
        the filesystems attribute of the class with the detail of
        all the filesystem present on the disk
        """
        self._filesystems = []
        for fs in self._client.btrfs.list():
            for device in fs['devices']:
                if device['path'] == "/dev/{}".format(self.name):
                    self._filesystems.append(fs)
                    break

    def _disk_type(self, disk_info):
        """
        return the type of the disk
        """
        if disk_info['rota'] == "1":
            if disk_info['model'].find('CD-ROM') != -1:
                return DiskType.cdrom
            # assume that if a disk is more than 7TB it's a SMR disk
            elif int(disk_info['size']) > (1024 * 1024 * 1024 * 1024 * 7):
                return DiskType.archive
            else:
                return DiskType.hdd
        else:
            if "nvme" in disk_info['name']:
                return DiskType.nvme
            else:
                return DiskType.ssd

    def mktable(self, table_type='gpt',  overwrite=False):
        """
        create a partition table on the disk
        @param table_type: Partition table type as accepted by parted
        @param overwrite: erase any existing partition table
        """
        if self.partition_table is not None and overwrite is False:
            return

        self._client.disk.mktable(
            disk=self.name,
            table_type=table_type
        )

    def mkpart(self, start, end, part_type="primary"):
        """
        @param start: partition start as accepted by parted mkpart
        @param end: partition end as accepted by parted mkpart
        @param part_type: partition type as accepted by parted mkpart
        """
        before = {p.name for p in self.partitions}

        self._client.disk.mkpart(
            self.name,
            start=start,
            end=end,
            part_type=part_type,
        )
        after = {}
        for disk in self._client.disk.list()['blockdevices']:
            if disk['name'] != self.name:
                continue
            for part in disk.get('children', []):
                after[part['name']] = part
        name = set(after.keys()) - before

        part_info = after[list(name)[0]]
        partition = Partition(
            client=self._client,
            disk=self,
            part_info=part_info)
        self.partitions.append(partition)

        return partition

    def mount(self, target, options=['defaults']):
        """
        @param target: Mount point
        @param options: Optional mount options
        """
        if self.mountpoint == target:
            return

        self._client.bash('mkdir -p {}'.format(target))

        self._client.disk.mount(
            source="/dev/{}".format(self.name),
            target=target,
            options=options,
        )
        self.mountpoint = target

    def umount(self):
        """
        Unmount disk
        """
        if self.mountpoint:
            self._client.disk.umount(
                source="/dev/{}".format(self.name),
            )
        self.mountpoint = None

    def __str__(self):
        return "Disk <{}>".format(self.name)

    def __repr__(self):
        return str(self)
