
from JumpScale import j

base = j.tools.cuisine._getBaseClass()

# TODO: *1 implement & test & document (test on packet.net)

# TODO: to implement this good first make sure there is a KVM SAL, then create jskvm just like ther eis a jsdocker
# see how we did for docker, we need same approach, make sure that in sal
# we expose all kvm/qemu properties e.g. limits from IOPS, ...
# make sure use click for the jskvm
# make sure we can also create/delete/list disks &

# use openvswitch inside (can use the sal directly in jskvm)

# this cuisine obj required jumpscale installed remotely otherwise jskvm is not accessible


# will have to change the kvm existing sal to be more modular for disks &
# nics (like we spec here) as well as use openvswitch

class CuisineKVMMachineObj():

    def __init__(self, kvm, name):
        self.kvm = kvm
        self._executor = kvm._executor
        self.cuisine = kvm._cuisine
        self.name = name
        self.vdiskNames = [...]
        self.vnicNames = [...]

    @property
    def mem(self):
        # get from reality
        raise NotImplemented()

    def start(self):
        # TODO:
        raise NotImplemented()

    def stop(self):
        # TODO:
        raise NotImplemented()

    def restart(self):
        # TODO:
        raise NotImplemented()

    @property
    def cuisine(self):
        # TODO: get cuisine connection into VM
        raise NotImplemented()

    def qos(self, **kwargs):
        """
        set vmachine QOS settings at runtime e.g. pinning to core?
        """
        # TODO: spec further
        raise NotImplemented()


class CuisineKVM(base):
    """
    usage:

    ```
    c=j.tools.cuisine.get("ovh4")
    c.systemservices.kvm.install()
    ```

    """

    def __init__(self, executor, cuisine):
        self._executor = executor
        self._cuisine = cuisine
        self._path = None
        self.__controller = None

    @property
    def _controller(self):
        if not self.__controller:
            if self._cuisine.id == 'localhost':
                host = 'localhost'
            else:
                host = '%s@%s'%(getattr(self._executor, '_login', 'root'), self._cuisine.id)
            self.__controller = j.sal.kvm.KVMController(
                host=host, executor=self._cuisine._executor)
        return self.__controller

    def download_image(self, url, overwrite=False):
        name = url.split('/')[-1]
        path = j.sal.fs.joinPaths(self._controller.base_path, 'images', name)
        self._controller.executor.cuisine.core.file_download(url, path, overwrite=True)

    def machine(self, name, os, disks, nics, memory, cpucount, uuid=None, cloud_init=True):
        return j.sal.kvm.CloudMachine(self._controller, name, os, disks, nics, memory, cpucount, uuid=None, cloud_init=True)

    def create_pool(self, name):
        pool = j.sal.kvm.Pool(self._controller, name)
        pool.create()
        return pool

    def create_network(self, name):
        network = j.sal.kvm.Network(self._controller, name)
        network.create()
        return network

    def prepare(self):
        self.install()

        # check openvswitch properly configured

    def install(self):
        if not self._cuisine.core.isUbuntu or self._cuisine.platformtype.osversion != '16.04':
            raise RuntimeError("only support ubuntu 16.04")
        self._libvirt()
        # check if kvm there if yes, don't do anything
        # do other required checks

    @property
    def path(self):
        if self._path is None:
            # look for btrfs fs kvm, is where all vm & disk info will be
            # TODO *1
            j.sal.fs.createDir(j.sal.fs.joinPaths(self._path, "vm"))
            j.sal.fs.createDir(j.sal.fs.joinPaths(self._path, "disk"))
        return self._path

    def vmGetPath(self, name):
        return j.sal.fs.joinPaths(self.path, "vm", name)

    def diskGetPath(self, name):
        return j.sal.fs.joinPaths(self.path, "disk", name)

    def _libvirt(self):
        """
        """
        # TODO: *1 need to check and exit if required are met
        self._cuisine.package.install('libvirt-bin')
        self._cuisine.package.install('libvirt-dev')
        self._cuisine.package.install('qemu-system-x86')
        self._cuisine.package.install('qemu-system-common')
        self._cuisine.package.install('genisoimage')
        self._cuisine.development.pip.install("libvirt-python==1.3.2", upgrade=False)

    def vdiskBootCreate(self, name, image='http://fs.aydo.com/kvm/ub_small.img'):
        path = j.sal.fs.joinPaths(self.diskStorPath, name)
        # create qcow2 image disk on the right path

    def vdiskCreate(self, pool, name, size=100, image_name=""):
        """
        @param size in GB
        """
        # create an empty disk we can attachl
        disk = j.sal.kvm.Disk(self._controller, pool, name, size, image_name)
        disk.create()

    def vdiskDelete(self, name):
        vol = self._controller.connection.get_volume(name)
        disk = j.sal.kvm.Disk.from_xml(self._controller, vol.XMLDesc())
        disk.delete()

    def vdisksList(self):
        storagecontroller = j.sal.kvm.StorageController(self._controller)
        disks = storagecontroller.list_disks()
        return disks

    def machineCreate(self, name, disks, nics, mem, pubkey=None):
        """
        @param disks is array of disk names (after using diskCreate)
        @param nics is array of nic names (after using nicCreate)


        will return kvmCuisineObj: is again a cuisine obj on which all kinds of actions can be executed

        @param pubkey is the key which will be used to get access to this kvm, if none then use the std ssh key as used for docker
        """
        # TODO: *1 implement & test

        # TODO: *1 test can access over ssh & push the ssh key, then change the std passwd

        # TODO: *1 create ssh portforward from this cuisine to localhost to allow access to ssh used by this kvm

        # NEED TO MAKE SURE WE CAN GET ACCESS TO THIS KVM WITHOUT OPENING PORTS
        # ON KVM HOST (which is current cuisine)

        return KVMMachineObj

    def vnicQOS(self, name, **kwargs):
        """
        set vnic QOS settings at runtime
        """
        raise NotImplemented()

    def vdiskQOS(self, name, **kwargs):
        """
        set vdisk QOS settings at runtime
        """
        raise NotImplemented()

    def vpoolCreate(self, name):
        pool = j.sal.kvm.StorageController(self._controller).get_or_create_pool(name)
        return pool

    def vpoolDestroy(self, name):
        j.sal.kvm.StorageController(self._controller).delete(name)
        return True

    def vmachinesList(self):
        machines = j.sal.kvm.controller.list_machines()
        return machines
