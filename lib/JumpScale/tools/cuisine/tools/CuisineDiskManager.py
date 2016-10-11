

from JumpScale import j
from JumpScale.sal.disklayout.DiskManager import DiskManager

base = j.tools.cuisine._getBaseClass()


class CuisineDiskManager(base):

    def __init__(self, executor, cuisine):
        self._executor = executor
        self._cuisine = cuisine

    def get(self):
        dm = DiskManager()
        dm.set_executor(self._executor)
        return dm
