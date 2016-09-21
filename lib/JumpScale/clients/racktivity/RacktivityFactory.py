from JumpScale import j
from energyswitch.client import RackSal


class RacktivityFactory:

    def __init__(self):
        self.__jslocation__ = "j.clients.racktivity"

    def getEnergySwitch(self, username, password, hostname, port, rtf=None, moduleinfo=None):
        return RackSal(username, password, hostname, port, rtf=None, moduleinfo=None)
