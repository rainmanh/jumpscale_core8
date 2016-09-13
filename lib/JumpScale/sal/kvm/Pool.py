from JumpScale import j
from BaseKVMComponent import BaseKVMComponent

class Pool(BaseKVMComponent):
    def __init__(self, controller, name):
        self.controller = controller
        self.name = name
        self.poolpath = self.controller.executor.cuisine.core.joinpaths(self.controller.base_path, self.name)
        self._lvpool = None


    def create(self):
        """
        Create the bool
        """

        self.controller.executor.cuisine.core.dir_ensure (self.poolpath)
        cmd = 'chattr +C %s ' % self.poolpath
        self.controller.executor.execute(cmd)
        self.controller.connection.storagePoolCreateXML(self.to_xml(), 0)

    def to_xml(self):
        """
        Export the pool to xml
        """
        
        pool = self.controller.get_template('pool.xml').render(
            pool_name=self.name, basepath=self.controller.base_path)
        return pool

    @property
    def lvpool(self):
        if not self._lvpool:
            self._lvpool = self.controller.connection.storagePoolLookupByName(self.name)
        return self._lvpool
