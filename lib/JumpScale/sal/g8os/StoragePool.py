from JumpScale.sal.g8os.abstracts import Mountable
import os


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
                    devicenames = [device['path'] for device in btrfs['devices']]
                    storagepools.append(StoragePool(self.node, name, devicenames))
        return storagepools

    def get(self, name):
        for pool in self.list():
            if pool.name == name:
                return pool
        raise ValueError("Could not find StoragePool with name {}".format(name))

    def create(self, name, devices, metadata_profile, data_profile):
        pool = StoragePool(self.node, name, devices)
        pool.create(metadata_profile, data_profile)
        return pool


class StoragePool(Mountable):
    def __init__(self, node, name, devices):
        self.node = node
        self._client = node._client
        self.devices = devices
        self.name = name
        self._mountpoint = None

    def create(self, metadata_profile, data_profile):
        label = 'sp_{}'.format(self.name)
        self._client.btrfs.create(label, self.devices, metadata_profile, data_profile)

    @property
    def devicename(self):
        return 'UUID={}'.format(self.uuid)

    @property
    def mountpoint(self):
        for device in self.devices:
            mountpoint = self._client.disk.getinfo(device[5:]).get('mountpoint')
            if mountpoint:
                return mountpoint

    @mountpoint.setter
    def mountpoint(self, value):
        # do not do anything mountpoint is dynamic
        return

    def _get_mountpoint(self):
        mountpoint = self.mountpoint
        if not mountpoint:
            raise RuntimeError("Can not perform subvol action when filesystem is not mounted")
        return mountpoint

    def list_subvolumes(self):
        subvolumes = []
        mountpoint = self._get_mountpoint()
        for subvolume in self._client.btrfs.subvol_list(mountpoint) or []:
            subvolumes.append(SubVolume(subvolume['Path'], self))
        return subvolumes

    def create_subvolume(self, name):
        mountpoint = self._get_mountpoint()
        subvolpath = os.path.join(mountpoint, name)
        self._client.btrfs.subvol_create(subvolpath)
        return SubVolume(name, self)

    def delete_subvolume(self, name):
        mountpoint = self._get_mountpoint()
        subvolpath = os.path.join(mountpoint, name)
        self._client.btrfs.subvol_delete(subvolpath)

    @property
    def filesystem(self):
        for fs in self._client.btrfs.list():
            if fs['label'] == 'sp_{}'.format(self.name):
                return fs
        return None

    @property
    def size(self):
        total = 0
        fs = self.filesystem
        if fs:
            for device in fs['devices']:
                total += device['size']
        return total

    @property
    def uuid(self):
        fs = self.filesystem
        if fs:
            return fs['uuid']
        return None

    @property
    def used(self):
        total = 0
        fs = self.filesystem
        if fs:
            for device in fs['devices']:
                total += device['used']
        return total

    def __repr__(self):
        return "StoragePool <{}>".format(self.name)


class SubVolume(Mountable):
    def __init__(self, name, pool):
        self.name = name
        self.pool = pool
        self._client = pool.node.client
        self.devicename = self.pool.devicename

    def mount(self, target, options=['defaults']):
        options.append('subvol={}'.format(self.name))
        return super().mount(target, options)

    @property
    def mountpoint(self):
        for mount in self.pool.node.list_mounts():
            mountopt = 'subvol=/{}'.format(self.name)
            if mount.device in self.pool.devices and mountopt in mount.options:
                return mount.mountpoint

    @mountpoint.setter
    def mountpoint(self, value):
        # do not do anything mountpoint is dynamic
        return

    def __repr__(self):
        return "SubVolume <{}: {!r}>".format(self.name, self.pool)
