from JumpScale import j
from .energyswitch.client import RackSal

class RacktivityFactory(object):

    def getEnergySwitch(self, username, password, hostname, port, rtf=None, moduleinfo=None):
        return RackSal(username, password, hostname, port, rtf=None, moduleinfo=None)
