from JumpScale import j
from xml.etree import ElementTree
from BaseKVMComponent import BaseKVMComponent
from Storage import Storage

class Disk(BaseKVMComponent):

    def __init__(self, controller, pool, name, size, image_name=""):
        self.size = size
        self.image_name = image_name
        self.controller = controller
        self.pool = pool
        self.name = name

    @classmethod
    def from_xml(cls, controller, diskxml):
        disk = ElementTree.fromstring(diskxml)
        name = disk.findtext('name')
        pool_name = disk.find('source').get('pool')
        pool = Storage(controller).get_pool(pool_name)
        size = disk.findtext('capacity')
        if disk.find('backingStore') is not None and disk.find('backingStore').find('source') is not None:
            path = disk.find('backingStore').find('source').get('file')
            image_name = path.split("/")[-1].split('.')[0]
        else:
            image_name = ''
        return cls(controller, pool, name, size,image_name)

    def to_xml(self):
        disktemplate = self.controller.get_template('disk.xml')
        if self.image_name:
            diskbasevolume = self.controller.executor.cuisine.core.joinpaths(self.controller.base_path, "images", '%s.qcow2' % self.image_name)
        else:
            diskbasevolume = ''
        diskpath = self.controller.executor.cuisine.core.joinpaths(self.pool.poolpath, '%s.qcow2' % self.name)
        diskxml = disktemplate.render({'diskname':self.name, 'diskpath': diskpath, 'disksize':self.size, 'diskbasevolume':diskbasevolume})
        return diskxml

    def create(self):
        volume = self.pool.lvpool.createXML(self.to_xml(), 0)
        #return libvirt volume obj
        return volume

    @property
    def is_created(self):
        # TODO
        return False

    def delete(self):
        try:
            volume = self.pool.storageVolLookupByName(self.name)
            volume.wipe(0)
            volume.destroy(0)
            return True
        except:
            return False

    def clone_disk(self, new_disk):
        volume = self.get_volume(self.name, pool)
        cloned_volume = self.pool.createXMLFrom(new_disk.to_xml(), disk, 0)
        return cloned_volume

    def get_volume(disk_name):
        try:
            volume = self.pool.storageVolLookupByName(disk_name)
            return volume
        except:
            return None
