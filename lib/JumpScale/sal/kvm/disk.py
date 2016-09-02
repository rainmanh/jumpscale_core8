from xml.etree import ElementTree
from jinja2 import Environment, PackageLoader, FileSystemLoader
from JumpScale import j
import os

class Disk():

    def __init__(self, controller, pool, vm_id, role, size, image_name=""):
        self.vm_id = vm_id
        self.role = role
        self.size = size
        self.image_name = image_name
        self.controller = controller
        self.pool = pool
        self.name = vm_id + '-' + self.role + '.qcow2'

    @classmethod
    def from_xml(cls, controller, diskxml):
        disk = ElementTree.fromstring(diskxml)
        name = disk.findtext('name')
        vm_id = name.split('-')[0]
        role = name.split('-')[0].split('.')[0]
        size = disk.findtext('size')
        path = disk.find('backingStore').findtext('path')
        image_name = path.split("/")[0].split('.')[0]
        return cls(controller, vm_id, role, size,image_name)

    def to_xml(self):
        disktemplate = self.controller.env.get_template('disk.xml')
        diskbasevolume = j.sal.fs.joinPaths(self.controller.template_path, '%s' % self.image_name)
        diskpath = j.sal.fs.joinPaths(self.pool.poolpath, '%s.qcow2' % self.name)
        diskxml = disktemplate.render({'diskname':self.name, 'diskpath': diskpath, 'disksize':self.size, 'diskbasevolume':diskbasevolume})
        return diskxml

    def create(self):
        volume = self.pool.lvpool.createXML(self.to_xml(), 0)
        #return libvirt volume obj
        return volume

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
        os.makedirs(self.poolpath)
        cmd = 'chattr +C %s ' % self.poolpath
        j.sal.process.execute(
            cmd, die=False, outputToStdout=False, useShell=False, ignoreErrorOutput=False)
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
    


class StorageController:

    def __init__(self, controller):
        self.controller = controller

    def get_pool(self, pool_name):
        try:
            storagepool = self.controller.connection.storagePoolLookupByName(pool_name)
            return storagepool
        except:
            return None

    def delete_pool(self, pootname):
        pool = self.get_pool(pool_name)
        if not pool is None:
            #destroy the pool
            pool.undefined()

    def get_or_create_pool(self, pool_name):
        if pool_name not in self.controller.connection.listStoragePools():
            poolpath = os.path.join(self.controller.base_path, pool_name)
            if not os.path.exists(poolpath):
                os.makedirs(poolpath)
                cmd = 'chattr +C %s ' % poolpath
                j.sal.process.execute(
                    cmd, die=False, outputToStdout=False, useShell=False, ignoreErrorOutput=False)
            pool = self.controller.env.get_template('pool.xml').render(
                pool_name=pool_name, basepath=self.controller.base_path)
            print(pool)
            self.controller.connection.storagePoolCreateXML(pool, 0)
        storagepool = self.controller.connection.storagePoolLookupByName(pool_name)
        return storagepool