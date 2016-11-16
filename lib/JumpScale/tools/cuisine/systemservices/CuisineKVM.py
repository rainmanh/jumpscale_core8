
from JumpScale import j

base = j.tools.cuisine._getBaseClass()

# TODO: to implement this good first make sure there is a KVM SAL, then create jskvm just like ther eis a jsdocker
# see how we did for docker, we need same approach, make sure that in sal
# we expose all kvm/qemu properties e.g. limits from IOPS, ...
# make sure use click for the jskvm

# this cuisine obj required jumpscale installed remotely otherwise jskvm is not accessible

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
            self.__controller = j.sal.kvm.KVMController(
                executor=self._cuisine._executor)
        return self.__controller

    def download_image(self, url, overwrite=False):
        name = url.split('/')[-1]
        path = j.sal.fs.joinPaths(self._controller.base_path, 'images', name)
        self._controller.executor.cuisine.core.file_download(url, path, overwrite=overwrite)

    def poolCreate(self, name):
        pool = j.sal.kvm.Pool(self._controller, name)
        pool.create()
        return pool

    def install(self):
        if not self._cuisine.core.isUbuntu or self._cuisine.platformtype.osversion != '16.04':
            raise RuntimeError("only support ubuntu 16.04")
        self._libvirt()

    @property
    def path(self):
        return self._controller.base_path

    def vmGetPath(self, name):
        return j.sal.fs.joinPaths(self.path, "vms", name)

    def iamgeGetPath(self, name):
        return j.sal.fs.joinPaths(self.path, "images", name)

    def _libvirt(self):
        """
        Install required packages for kvm
        """
        self._cuisine.package.install('libvirt-bin')
        self._cuisine.package.install('libvirt-dev')
        self._cuisine.package.install('qemu-system-x86')
        self._cuisine.package.install('qemu-system-common')
        self._cuisine.package.install('genisoimage')
        self._cuisine.development.pip.install("libvirt-python==1.3.2", upgrade=False)

    def vdiskBootCreate(self, name, image='http://fs.aydo.com/kvm/ub_small.img'):
        path = j.sal.fs.joinPaths(self._controller.base_path, 'images', name)
        self._controller.executor.cuisine.core.file_download(image, path, overwrite=True)

    def vdiskCreate(self, pool, name, size=100, image_path=""):
        """
        create an empty disk we can attachl
        @param size in GB
        """
        disk = j.sal.kvm.Disk(self._controller, pool, name, size, image_path)
        disk.create()

    def vdiskDelete(self, name):
        vol = self._controller.connection.get_volume(name)
        disk = j.sal.kvm.Disk.from_xml(self._controller, vol.XMLDesc())
        disk.delete()

    def vdisksList(self):
        storagecontroller = j.sal.kvm.StorageController(self._controller)
        disks = storagecontroller.list_disks()
        return disks

    def machineCreate(self, name, os='xenial-server-cloudimg-amd64-uefi1.img', disks=[10],
            nics=['vms1'], memory=2000, cpucount=4, cloud_init=True, start=True, resetPassword=True):
        """
        @param disks is array of disk names (after using diskCreate)
        @param nics is array of nic names (after using nicCreate)


        will return kvmCuisineObj: is again a cuisine obj on which all kinds of actions can be executed

        @param pubkey is the key which will be used to get access to this kvm, if none then use the std ssh key as used for docker
        """
        machine = j.sal.kvm.CloudMachine(self._controller, name, os, disks,
            nics, memory, cpucount, cloud_init=cloud_init)

        machine.create()

        if start:
            machine.start()
            if resetPassword:
                machine.cuisine.core.sudo("echo '%s:%s' | chpasswd"%(
                    getattr(machine.executor, 'login', 'root'),
                    j.data.idgenerator.generatePasswd(10).replace("'", "'\"'\"'")))

        return machine

    def get_machine_by_name(self, name):
        return j.sal.kvm.Machine.get_by_name(self._controller, name)

    def vpoolCreate(self, name):
        pool = j.sal.kvm.StorageController(self._controller).get_or_create_pool(name)
        return pool

    def vpoolDestroy(self, name):
        j.sal.kvm.StorageController(self._controller).delete(name)
        return True

    def vmachinesList(self):
        machines = j.sal.kvm.controller.list_machines()
        return machines
