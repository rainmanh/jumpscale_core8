

from JumpScale import j
from JumpScale.sal.disklayout.DiskManager import DiskManager

base = j.tools.cuisine._getBaseClass()


class CuisineDiskManager(base):

    def get(self):
        dm = DiskManager()
        dm.set_executor(self.executor)
        dm.getDisks()
        return dm
