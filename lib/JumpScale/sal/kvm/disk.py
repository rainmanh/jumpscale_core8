from xml.etree import ElementTree
from jinja2 import Environment, PackageLoader, FileSystemLoader
from JumpScale import j
import os

class Disk():

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
        pool_name = disk.find('target').findtext('path').split("/")[-2]
        pool = StorageController(controller).get_pool(pool_name)
        size = disk.findtext('capacity')
        #TODO optional image
        if not disk.find('backingStore') is None:
            path = disk.find('backingStore').findtext('path')
            image_name = path.split("/")[0].split('.')[0]
        else:
            image_name = ''
        return cls(controller, pool, name, size,image_name)

    def to_xml(self):
        disktemplate = self.controller.env.get_template('disk.xml')
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


class Pool:
    def __init__(self, controller, name):
        self.controller = controller
        self.name = name
        self.poolpath = os.path.join(self.controller.base_path, self.name)
        self._lvpool = None


    def create(self):
        self.controller.executor.cuisine.core.dir_ensure (self.poolpath)
        cmd = 'chattr +C %s ' % self.poolpath
        self.controller.executor.execute(cmd)
        self.controller.connection.storagePoolCreateXML(self.to_xml(), 0)

    def to_xml(self):
        pool = self.controller.env.get_template('pool.xml').render(
            pool_name=self.name, basepath=self.controller.base_path)
        return pool

    @property
    def lvpool(self):
        if not self._lvpool:
            self._lvpool = self.controller.connection.storagePoolLookupByName(self.name)
        return self._lvpool



class Storage:

    def __init__(self, controller):
        self.controller = controller

    def get_pool(self, pool_name):
        try:
            storagepool = self.controller.connection.storagePoolLookupByName(pool_name)
            return storagepool
        except:
            return None

    def create_pool(self, pool):
        self.controller.executor.cuisine.core.dir_ensure (pool.poolpath)
        cmd = 'chattr +C %s ' % pool.poolpath
        self.controller.executor.execute(cmd)
        self.controller.connection.storagePoolCreateXML(pool.to_xml(), 0)


    def delete_pool(self, pootname):
        pool = self.get_pool(pool_name)
        if not pool is None:
            #destroy the pool
            pool.undefined()

    def get_or_create_pool(self, pool_name):
        if pool_name not in self.controller.connection.listStoragePools():
            poolpath = os.path.join(self.controller.base_path, pool_name)
            if not self.controller.executor.cuisine.core.dir_exists(poolpath):
                self.controller.executor.cuisine.core.dir_ensure(poolpath)
                cmd = 'chattr +C %s ' % poolpath
                self.controller.executor.execute(cmd)
            pool = self.controller.env.get_template('pool.xml').render(
                pool_name=pool_name, basepath=self.controller.base_path)
            print(pool)
            self.controller.connection.storagePoolCreateXML(pool, 0)
        storagepool = self.controller.connection.storagePoolLookupByName(pool_name)
        return storagepool

    def list_disks(self):
        disks = []
        for pool in self.controller.connection.listAllStoragePools():
            if pool.isActive():
                for vol in pool.listAllVolumes():
                    disk = Disk.from_xml(self.controller, vol.XMLDesc())
                    disks.append(disk)
        return disks
