import re



from JumpScale import j
from . import mount
from . import lsblk



_formatters = {
    # specific format command per filesystem.
    'ntfs': lambda name, fstype: 'mkfs.ntfs -f {name}'.format(name=name)
}

isValidFS = lambda v: v.startswith('ext') or v in ('btrfs', 'ntfs')

_hrd_validators = {
    'filesystem': isValidFS
}


def _default_formatter(name, fstype):
    return 'mkfs.{fstype} {name}'.format(
        fstype=fstype,
        name=name
    )


class BlkInfo(object):
    def __init__(self,  name, type, size):
        self.name = name
        self.type = type
        self.size = int(size)

    def __str__(self):
        return '%s %s' % (self.name, self.size)

    def __repr__(self):
        return str(self)


class DiskInfo(BlkInfo):
    """
    Represents a disk
    """
    def __init__(self,  name, size):
        super(DiskInfo, self).__init__(name, 'disk', size)
        self.partitions = list()
        self._executor = j.tools.executor.getLocal()

    def _getpart(self):
        rc, ptable = self._executor.execute(
            'parted -sm {name} unit B print'.format(name=self.name)
        )
        read_disk_next = False
        disk = {}
        partitions = []
        for line in ptable.split('\n'):
            line = line.strip()
            if line == 'BYT;':
                read_disk_next = True
                continue

            parts = line.split(':')
            if read_disk_next:
                # /dev/sdb:8589934592B:scsi:512:512:gpt:ATA VBOX HARDDISK;
                size = int(parts[1][:-1])
                table = parts[5]

                disk.update(
                    size=size,
                    table=table,
                )
                read_disk_next = False
                continue

            # 1:1048576B:2097151B:1048576B:btrfs:primary:;
            partition = {
                'number': int(parts[0]),
                'start': int(parts[1][:-1]),
                'end': int(parts[2][:-1]),
            }

            partitions.append(partition)

        disk['partitions'] = partitions
        return disk

    def _findFreeSpot(self, parts, size):
        if size > parts['size']:
            return
        start = 20 * 1024  # start from 20k offset.
        for partition in parts['partitions']:
            if partition['start'] - start > size:
                return start, start + size
            start = partition['end'] + 1

        if start + size > parts['size']:
            return

        return start, start + size

    def _validateHRD(self, hrd):
        for field in ['filesystem', 'mountpath', 'protected', 'type']:
            if not hrd.exists(field):
                raise PartitionError(
                    'Invalid hrd, missing mandatory field "%s"' % field
                )
            if field in _hrd_validators:
                validator = _hrd_validators[field]
                value = hrd.get(field)
                if not validator(value):
                    raise PartitionError('Invalid valud for %s: %s' % (
                        field, value
                    ))

    def format(self, size, hrd):
        """
        Create new partition and format it as configured in hrd file

        :size: in bytes
        :hrd: the disk hrd info

        Note:
        hrd file must contain the following

        filesystem                     = '<fs-type>'
        mountpath                      = '<mount-path>'
        protected                      = 0 or 1
        type                           = data or root or tmp
        """
        self._validateHRD(hrd)

        if not self.partitions:
            # if no partitions, make sure to clear mbr to convert to gpt
            self._clearMBR()

        parts = self._getpart()
        spot = self._findFreeSpot(parts, size)
        if not spot:
            raise Exception('No enough space on disk to allocate')

        start, end = spot
        try:
            j.do.execute(
                ('parted -s {name} unit B ' +
                    'mkpart primary {start} {end}').format(name=self.name,
                                                           start=start,
                                                           end=end)
            )
        except Exception as e:
            raise FormatError(e)

        numbers = [p['number'] for p in parts['partitions']]
        newparts = self._getpart()
        newnumbers = [p['number'] for p in newparts['partitions']]
        number = list(set(newnumbers).difference(numbers))[0]

        partition = PartitionInfo(
            name='%s%d' % (self.name, number),
            size=size,
            uuid='',
            fstype='',
            mount=''
        )

        partition.hrd = hrd

        partition.format()
        self.partitions.append(partition)
        return partition

    def _clearMBR(self):
        try:
            j.do.execute(
                'parted -s {name} mktable gpt'.format(name=self.name)
            )
        except Exception as e:
            raise DiskError(e)

    def erase(self, force=False):
        """
        Clean up disk by deleting all non protected partitions
        if force=True, delete ALL partitions included protected

        :force: delete protected partitions, default=False
        """
        if force:
            self._clearMBR()
            return

        for partition in self.partitions:
            if not partition.protected:
                partition.delete()


class PartitionInfo(BlkInfo):
    def __init__(self,  name, size, uuid, fstype, mount):
        super(PartitionInfo, self).__init__(name, 'part', size)
        self.uuid = uuid
        self.fstype = fstype
        self.mountpoint = mount
        self.hrd = None

        self._invalid = False

    @property
    def invalid(self):
        return self._invalid

    @property
    def protected(self):
        if self.hrd is None:
            # that's an unmanaged partition, assume protected
            return True

        return bool(self.hrd.get('protected', True))

    def _formatter(self, name, fstype):
        fmtr = _formatters.get(fstype, _default_formatter)
        return fmtr(name, fstype)

    def refresh(self):
        """
        Reload partition status to match current real state
        """
        try:
            info = lsblk.lsblk(self.name)[0]
        except lsblk.LsblkError:
            self._invalid = True
            info = {
                'SIZE': 0,
                'UUID': '',
                'FSTYPE': '',
                'MOUNTPOINT': ''
            }

        for key, val in info.items():
            setattr(self, key.lower(), val)

    def _dumpHRD(self):
        with mount.Mount(self.name) as mnt:
            filepath = j.tools.path.get(mnt.path).joinpath('.disk.hrd')
            filepath.write_text(str(self.hrd))
            filepath.chmod(400)

    def format(self):
        """
        Reformat the partition according to hrd
        """
        if self.invalid:
            raise PartitionError('Partition is invalid')

        if self.mountpoint:
            raise PartitionError(
                'Partition is mounted on %s' % self.mountpoint
            )

        if self.hrd is None:
            raise PartitionError('No HRD attached to disk')

        fstype = self.hrd.get('filesystem')
        command = self._formatter(self.name, fstype)
        try:
            self._executor.execute(command)
            self._dumpHRD()
        except Exception as e:
            raise FormatError(e)

        self.refresh()

    def delete(self, force=False):
        """
        Delete partition

        :force: Force delete protected partitions, default False
        """
        if self.invalid:
            raise PartitionError('Partition is invalid')

        if self.mountpoint:
            raise PartitionError(
                'Partition is mounted on %s' % self.mountpoint
            )

        if self.protected and not force:
            raise PartitionError('Partition is protected')

        m = re.match('^(.+)(\d+)$', self.name)
        number = int(m.group(2))
        device = m.group(1)

        command = 'parted -s {device} rm {number}'.format(
            device=device,
            number=number
        )
        try:
            self._executor.execute(command)
        except Exception as e:
            raise PartitionError(e)

        self.unsetAutoMount()

        self._invalid = True

    def mount(self):
        """
        Mount partition to `mountpath` defined in HRD
        """
        if self.invalid:
            raise PartitionError('Partition is invalid')

        if self.hrd is None:
            raise PartitionError('No HRD attached to disk')

        path = self.hrd.get('mountpath')
        mnt = mount.Mount(self.name, path)
        mnt.mount()
        self.refresh()

    def umount(self):
        """
        Unmount partition
        """
        if self.invalid:
            raise PartitionError('Partition is invalid')

        if self.hrd is None:
            raise PartitionError('No HRD attached to disk')

        path = self.hrd.get('mountpath')
        mnt = mount.Mount(self.name, path)
        mnt.umount()
        self.refresh()

    def unsetAutoMount(self):
        """
        remote partition from fstab
        """
        fstabpath = j.tools.path.get('/etc/fstab')
        fstab = fstabpath.text().split('\n')
        dirty = False

        for i in range(len(fstab) - 1, -1, -1):
            line = fstab[i]
            if line.startswith('UUID=%s' % self.uuid):
                del fstab[i]
                dirty = True

        if not dirty:
            return

        fstabpath.write_text('\n'.join(fstab))
        fstabpath.chmod(644)

    def setAutoMount(self, options='defaults', _dump=0, _pass=0):
        """
        Configure partition auto mount `fstab` on `mountpath` defined in HRD
        """
        path = j.tools.path.get(self.hrd.get('mountpath'))
        path.makedirs_p()

        fstabpath = j.tools.path.get('/etc/fstab')
        fstab = fstabpath.text().split('\n')
        dirty = False

        try:
            for i in range(len(fstab) - 1, -1, -1):
                line = fstab[i]
                if line.startswith('UUID=%s' % self.uuid):
                    del fstab[i]
                    dirty = True
                    break

            if path is None:
                return

            entry = ('UUID={uuid}\t{path}\t{fstype}' +
                     '\t{options}\t{_dump}\t{_pass}').format(
                uuid=self.uuid,
                path=path,
                fstype=self.fstype,
                options=options,
                _dump=_dump,
                _pass=_pass
            )

            fstab.append(entry)
            dirty = True
        finally:
            if not dirty:
                return

            fstabpath.write_text('\n'.join(fstab)),
            fstabpath.chmod(644)
