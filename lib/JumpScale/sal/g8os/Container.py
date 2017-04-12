class Container:
    """G8SO Container"""

    def __init__(self, name, node, flist, hostname=None, filesystems=None, nics=None, host_network=False, ports=None, storage=None):
        """
        TODO: write doc string
        filesystems: dict {filesystemObj: target}
        """
        self.name = name
        self.node = node
        self.filesystems = filesystems or {}
        self.hostname = hostname
        self.flist = flist
        self.ports = ports or {}
        self.nics = nics or []
        self.host_network = host_network
        self.storage = storage
        self.id = None
        self._client = None

        self._ays = None

    @classmethod
    def from_ays(cls, service):
        from JumpScale.sal.g8os.Node import Node
        node = Node.from_ays(service.parent)
        ports = {}
        for portmap in service.model.data.ports:
            source, dest = portmap.split(':')
            ports[int(source)] = int(dest)
        nics = [nic.to_dict() for nic in service.model.data.nics]

        container = cls(
            name=service.name,
            node=node,
            # filesystems = service.model.data. TODO
            nics=nics,
            hostname=service.model.data.hostname,
            flist=service.model.data.flist,
            ports=ports,
            host_network=service.model.data.hostNetworking,
            storage=service.model.data.storage
        )
        if service.model.data.id != 0:
            container.id = service.model.data.id

        return container

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
            nics=self.nics,
            port=self.ports,
            hostname=self.hostname,
            storage=self.storage,
        )
        self._client = self.node.client.container.client(self.id)

    def start(self):
        if not self.is_running():
            self._create_container()

    def stop(self):
        if not self.is_running():
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
