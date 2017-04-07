from JumpScale import j
import io
import time


class Container:
    """G8SO Container"""

    def __init__(self, name, node, flist, hostname=None, filesystems={}, zerotier=None, host_network=False, ports={}, storage='ardb://hub.gig.tech:16379'):
        """
        TODO: write doc string
        filesystems: dict {filesystemObj: target}
        """
        self.name = name
        self.node = node
        self.filesystems = filesystems
        self.hostname = hostname
        self.flist = flist
        self.zerotier = zerotier
        self.ports = ports
        self.host_network = host_network
        self.storage = storage
        self.id = None
        self._client = None

        self._ays = None

    @classmethod
    def from_ays(cls, service):
        from JumpScale.sal.g8os.Node import Node
        node = Node.from_ays(service.parent)
        return cls(
            name=service.name,
            node=node,
            # filesystems = service.model.data. TODO
            hostname=service.model.data.hostname,
            flist=service.model.data.flist,
            zerotier=service.model.data.zerotier,
            # ports = service.model.data.port. TODO
            host_network=service.model.data.hostNetworking,
            storage=service.model.data.storage
        )

    @property
    def client(self):
        if self._client is None:
            self._client = self.node.client.container.client(self.id)
        return self._client

    def _create_container(self):
        mounts = {}
        for fs, target in self.filesystems.items():
            mounts[fs.path] = target

        self.id = self.node.client.container.create(
            root_url=self.flist,
            mount=mounts,
            host_network=self.host_network,
            zerotier=self.zerotier,
            bridge=None,
            port=self.ports,
            hostname=self.hostname,
            storage=self.storage,
        )
        self._client = self.node.client.container.client(self.id)

    def start(self, timeout=30):
        if self.id is None:
            self._create_container()

    def stop(self, timeout=30):
        if self.id is None:
            return

        self.node.client.container.terminate(self.id)
        self._client = None
        self.id = None

    def is_running(self):
        if self.id is None:
            return False
        return self.id in map(int, self.node.client.container.list().keys())

    @property
    def ays(self):
        if self._ays is None:
            from JumpScale.sal.g8os.atyourservice.StorageCluster import ContainerAYS
            self._ays = ContainerAYS(self)
        return self._ays
