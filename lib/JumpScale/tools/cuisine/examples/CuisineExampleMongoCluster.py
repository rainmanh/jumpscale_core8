
from JumpScale import j

base = j.tools.cuisine._getBaseClass()

# TODO: *1 implement & test & document (test on packet.net)


class CuisineExampleMongoCluster(base):

    def __init__(self, executor, cuisine):
        self._executor = executor
        self._cuisine = cuisine

    def install(self, pubkey=None):
        c = self._cuisine

        # TODO: for this to work we need small KVM image somewhere in which docker
        # is preconfigured & jumpscale inside with our G8OS fuse layer (to keep
        # image small), host this image & use as standard when creating KVM
        # this image is autobuilded using our docker build system !!!

        # check is ubuntu TODO:

        # make sure kvm gets installed on the node
        c.systemservices.kvm.install()  # give size, ...

        kvm1 = c.systemservices.kvm.machineCreate("kvm1")
        kvm2 = c.systemservices.kvm.machineCreate("kvm2")

        # create dockers which will be used to create mongocluster with
        nodes = []
        for i in range(5):
            nodes.append(kvm1.systemservices.docker.start("n%s" % i, pubkey=pubkey, weave=True))
        for i in range(5):
            nodes.append(kvm2.systemservices.docker.start("n%s" % i, pubkey=pubkey, weave=True))

        # result is 10 nodes which are connected over weave & they can tak to each other over weave

        # TODO: complete example to create a mongo cluster over these 10 nodes
