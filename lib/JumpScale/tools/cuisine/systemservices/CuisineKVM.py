
from JumpScale import j

base = j.tools.cuisine._getBaseClass()

# TODO: *1 implement & test & document (test on packet.net)

# TODO: to implement this good first make sure there is a KVM SAL, then create jskvm just like ther eis a jsdocker
# see how we did for docker, we need same approach, make sure that in sal
# we expose all kvm/wemu properties e.g. limits from IOPS, ...


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

    def install(self):
        if self._cuisine.core.isUbuntu:
            # TODO: check is ubuntu 16.04
            raise NotImplemented
        else:
            raise RuntimeError("only support ubuntu")

    def _libvirt(self):
        """
        """
        # TODO: need to check and exit if required are met *1
        self._cuisine.package.install('libvirt-dev')
        self._cuisine.development.pip.install("libvirt-python==1.3.2", upgrade=False)

    def machineCreate(self, name="ubuntu1", image='http://fs.aydo.com/kvm/ub_small.img', pubkey=None):
        """

        #TODO: *1 need other arguments like mem, ... (all useful libvirt params)

        will return kvmCuisineObj: is again a cuisine obj on which all kinds of actions can be executed

        @param pubkey is the key which will be used to get access to this kvm, if none then use the std ssh key as used for docker
        """
        # TODO: *1 implement & test

        # TODO: *1 test can access over ssh & push the ssh key, then change the std passwd

        # TODO: *1 create ssh portforward from this cuisine to localhost to allow access to ssh used by this kvm

        # NEED TO MAKE SURE WE CAN GET ACCESS TO THIS KVM WITHOUT OPENING PORTS
        # ON KVM HOST (which is current cuisine)

        return kvmCuisineObj
