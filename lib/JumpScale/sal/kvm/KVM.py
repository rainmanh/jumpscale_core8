from JumpScale import j
from vnic import *
from disk import *
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
        self.Storage = Storage
        self.CloudMachine = CloudMachine
