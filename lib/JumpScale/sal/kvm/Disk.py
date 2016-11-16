from JumpScale import j
from xml.etree import ElementTree
from BaseKVMComponent import BaseKVMComponent
from StorageController import StorageController


class Disk(BaseKVMComponent):
    """
    Wrapper class around libvirt's storage volume object , to use with jumpscale libs.
    """

    def __init__(self, controller, pool, name, size, image_path="", disk_iops=None):
        """
        Disk object instance.

        @param controller object(j.sal.kvm.KVMController()): controller object to use.
        @param pool str: name of the pool to add disk to.
        @param name str: name of the disk.
        @param size int: size of disk in Mb.
        @param image_path  str: name of image to load on disk  if available.
        @param disk_iops int: total throughput limit in bytes per second.
        """
        self.size = size
        self.image_path = image_path
        self.controller = controller
        self.pool = pool
        self.name = name
        self.disk_iops = int(disk_iops) if disk_iops else None

    @classmethod
    def from_xml(cls, controller, diskxml):
        """
        Create Disk object from xml.

        @controller object(j.sal.kvm.KVMController()): controller object to use.
        @diskxml str: xml representation of the disk
        """

        disk = ElementTree.fromstring(diskxml)
        name = disk.findtext('name')
        pool_name = disk.find('source').get('pool')
        pool = StorageController(controller).get_pool(pool_name)
        size = disk.findtext('capacity')
        if disk.find('backingStore') is not None and disk.find('backingStore').find('source') is not None:
            image_path = disk.find('backingStore').find('source').get('file')
        else:
            image_path = ''
        return cls(controller, pool, name, size, image_path)

    def to_xml(self):
        """
        Export disk object to xml
        """

        disktemplate = self.controller.get_template('disk.xml')
        diskpath = self.controller.executor.cuisine.core.joinpaths(self.pool.poolpath, '%s.qcow2' % self.name)
        diskxml = disktemplate.render({'diskname': self.name, 'diskpath': diskpath,
                                       'disksize': self.size, 'diskbasevolume': self.image_path})
        return diskxml

    def create(self):
        """
        Create the actual volume in libvirt
        """

        volume = self.pool.lvpool.createXML(self.to_xml(), 0)
        # return libvirt volume obj
        return volume

    @property
    def is_created(self):
        """
        Check if the disk is created (defined) in libvirt
        """

        # TODO
        return False

    def delete(self):
        """
        Delete the disk
        """

        try:
            volume = self.pool.storageVolLookupByName(self.name)
            volume.wipe(0)
            volume.destroy(0)
            return True
        except:
            return False

    def clone_disk(self, new_disk):
        """
        Clone the disk
        """

        volume = self.get_volume(self.name, pool)
        cloned_volume = self.pool.createXMLFrom(new_disk.to_xml(), disk, 0)
        return cloned_volume

    def get_volume(self, disk_name):
        """
        Return libvirt's storage volume instance with disk_name if created.

        @param disk_name str: disk name to search for.
        """
        try:
            volume = self.pool.storageVolLookupByName(disk_name)
            return volume
        except:
            return None
