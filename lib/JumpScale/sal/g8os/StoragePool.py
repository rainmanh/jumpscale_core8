from JumpScale.sal.g8os.abstracts import Mountable


class StoragePools:
    def __init__(self, node):
        self.node = node
        self._client = node._client

    def list(self):
        storagepools = []
        btrfs_list = self._client.btrfs.list()
        if btrfs_list:
            for btrfs in self._client.btrfs.list():
                if btrfs['label'].startswith('sp_'):
                    name = btrfs['label'].split('_', 1)[1]
                    devicenames = [device['path'] for device in sorted(btrfs['devices'], key=lambda dev: dev['dev_id'])]
                    storagepools.append(StoragePool(self, name, devicenames, uuid=btrfs['uuid']))
        return storagepools

    def get(self, name):
        for pool in self.list():
            if pool.name == name:
                return pool
        raise ValueError("Could not find StoragePool with name {}".format(name))

    def create(self, name, devices, metadata_profile, data_profile):
        pool = StoragePool(self.node, name, devices, metadata_profile, data_profile)
        pool.create()
        return pool


class StoragePool(Mountable):
    def __init__(self, node, name, devices,
                 metadata_profile=None, data_profile=None,
                 uuid=None, status=None):
        self.node = node
        self._client = node._client
        self.devices = devices
        self.name = name
        self.metadata_profile = metadata_profile
        self.data_profile = data_profile
        self.uuid = uuid
        self.status = status
        self.mountpoint = None

    def create(self):
        label = 'sp_{}'.format(self.name)
        self._client.btrfs.create(label, self.devices, self.metadata_profile, self.data_profile)

    @property
    def devicename(self):
        return self.devices[0]
