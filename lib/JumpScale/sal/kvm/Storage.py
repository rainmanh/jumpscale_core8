from JumpScale import j
from BaseKVMComponent import BaseKVMComponent

class Storage(BaseKVMComponent):

    def __init__(self, controller):
        self.controller = controller

    def get_pool(self, pool_name):
        """
        Get pool
        """

        try:
            storagepool = self.controller.connection.storagePoolLookupByName(pool_name)
            return storagepool
        except:
            return None

    def create_pool(self, pool):
        """
        @pool pool: pool object to create pool from
        Create pool in libvirt
        """

        self.controller.executor.cuisine.core.dir_ensure (pool.poolpath)
        cmd = 'chattr +C %s ' % pool.poolpath
        self.controller.executor.execute(cmd)
        self.controller.connection.storagePoolCreateXML(pool.to_xml(), 0)


    def delete_pool(self, pootname):
        """
        Delet pool
        """

        pool = self.get_pool(pool_name)
        if not pool is None:
            #destroy the pool
            pool.undefined()

    def get_or_create_pool(self, pool_name):
        """
        get or create bool if it does not exists
        """

        if pool_name not in self.controller.connection.listStoragePools():
            poolpath = self.controller.executor.cuisine.core.joinpaths(self.controller.base_path, pool_name)
            if not self.controller.executor.cuisine.core.dir_exists(poolpath):
                self.controller.executor.cuisine.core.dir_ensure(poolpath)
                cmd = 'chattr +C %s ' % poolpath
                self.controller.executor.execute(cmd)
            pool = self.controller.get_template('pool.xml').render(
                pool_name=pool_name, basepath=self.controller.base_path)
            print(pool)
            self.controller.connection.storagePoolCreateXML(pool, 0)
        storagepool = self.controller.connection.storagePoolLookupByName(pool_name)
        return storagepool

    def list_disks(self):
        """
        List all disks from all pools
        """

        disks = []
        for pool in self.controller.connection.listAllStoragePools():
            if pool.isActive():
                for vol in pool.listAllVolumes():
                    disk = Disk.from_xml(self.controller, vol.XMLDesc())
                    disks.append(disk)
        return disks
