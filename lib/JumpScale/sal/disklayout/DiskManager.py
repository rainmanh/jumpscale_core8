from JumpScale import j
import lsblk
import mount
import disks

from sal.base.SALObject import SALObject


class DiskManager():
    def __init__(self):
        self.__jslocation__ = "j.sal.disklayout"

    def _loadhrd(self, mount):
        hrdpath = j.tools.path.get(mount).joinpath('.disk.hrd')
        if hrdpath.exists():
            return j.data.hrd.get(hrdpath)

    def _loaddisks(self, blks):
        """
        Parses the output of command
        `lsblk -abnP -o NAME,TYPE,UUID,FSTYPE,SIZE`

        Output must look like that
        NAME="sda" TYPE="disk" UUID="" FSTYPE="" SIZE="256060514304"
        NAME="sda1" TYPE="part" UUID="1db378f5-4e49-4fb7-8000-051fe77b23ea"
            FSTYPE="btrfs" SIZE="256059465728"
        NAME="sr0" TYPE="rom" UUID="" FSTYPE="" SIZE="1073741312"
        """
        devices = []
        disk = None
        for blk in blks:
            name = blk['NAME']
            if blk['TYPE'] == 'disk':
                disk = disks.DiskInfo(name, blk['SIZE'])
                devices.append(disk)
            elif blk['TYPE'] == 'part':
                if disk is None:
                    raise Exception(
                        ('Parition "%s" does not have a parent disk' %
                            blk['NAME'])
                    )
                part = disks.PartitionInfo(
                    name, blk['SIZE'],
                    blk['UUID'], blk['FSTYPE'],
                    blk['MOUNTPOINT']
                )
                disk.partitions.append(part)
            else:
                # don't care about outher types.
                disk = None

        return devices

    def getDisks(self,detailed=None):
        """
        Get list of all available disks on machine
        """
        blks = lsblk.lsblk()
        devices = self._loaddisks(blks)
        # loading hrds
        for disk in devices:
            for partition in disk.partitions:
                if partition.fstype == 'swap' or\
                        not disks.isValidFS(partition.fstype):
                    continue

                if partition.mountpoint and partition.fstype != 'btrfs':
                    # partition is already mounted, no need to remount it
                    hrd = self._loadhrd(partition.mountpoint)
                elif partition.fstype:
                    with mount.Mount(partition.name,
                                     options='ro') as mnt:
                        hrd = self._loadhrd(mnt.path)

                partition.hrd = hrd
        if detailed:
           return blks
        else:
            return devices

