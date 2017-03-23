class Partition:
    """Partition of a disk in a G8OS"""

    def __init__(self, client, disk, part_info):
        """
        part_info: dict returned by client.disk.list()
        """
        # g8os client to talk to the node
        self._client = client
        self.disk = disk
        self.name = None
        self.size = None
        self.blocksize = None
        self.mountpoint = None
        self._filesystems = []

        self._load(part_info)

    @property
    def filesystems(self):
        self._populate_filesystems()
        return self._filesystems

    def _load(self, part_info):
        detail = self._client.disk.getinfo(self.disk.name, part_info['name'])
        self.name = part_info['name']
        self.size = int(part_info['size'])
        self.blocksize = detail['blocksize']
        self.mountpoint = part_info['mountpoint']

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
        return "Partition <{}>".format(self.name)

    def __repr__(self):
        return str(self)
