from JumpScale import j
from Network import Network
from Interface import Interface
from Disk import Disk
from Pool import Pool
from StorageController import StorageController
from KVMController import KVMController
from Machine import Machine
from CloudMachine import CloudMachine
from MachineSnapshot import MachineSnapshot


class KVM:

    def __init__(self):

        self.__jslocation__ = "j.sal.kvm"
        self.KVMController = KVMController
        self.Machine = Machine
        self.MachineSnapshot = MachineSnapshot
        self.Network = Network
        self.Interface = Interface
        self.Disk = Disk
        self.Pool = Pool
        self.StorageController = StorageController
        self.CloudMachine = CloudMachine
