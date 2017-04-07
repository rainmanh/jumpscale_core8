from JumpScale.sal.g8os.abstracts import AYSable
from JumpScale.sal.g8os.StorageCluster import StorageCluster


def _node_name(node):
    for nic in node.client.info.nic():
        for addr in nic['addrs']:
            if addr['addr'].split('/')[0] == node.addr:
                return nic['hardwareaddr'].replace(':', '')
    raise AttributeError("name not find for node {}".format(node))


class StorageClusterAys(AYSable):

    def __init__(self, storagecluster):
        self._obj = storagecluster
        self.actor = 'storage_cluster'

    def create(self, aysrepo):
        # create all producers
        producers = []

        for fs in self._obj.filesystems:
            try:
                pool_service = fs.pool.ays.get(aysrepo)
            except ValueError:
                pool_service = fs.pool.ays.create(aysrepo)

            try:
                fs_service = fs.ays.get(aysrepo)
            except ValueError:
                fs_service = fs.ays.create(aysrepo)
            fs_service.consume(pool_service)
            producers.append(fs_service)

        for server in self._obj.storage_servers:
            try:
                container_service = server.container.ays.get(aysrepo)
            except ValueError:
                container_service = server.container.ays.create(aysrepo)

            try:
                ardb_services = server.ardb.ays.get(aysrepo)
            except ValueError:
                ardb_services = server.ardb.ays.create(aysrepo)
            ardb_services.consume(container_service)
            producers.append(ardb_services)

        actor = aysrepo.actorGet(self.actor)
        args = {
            'label': self._obj.name,
            # 'status':
            'nrServer': self._obj.nr_server,
            'hasSlave': self._obj.has_slave,
            'diskType': str(self._obj.disk_type),
            'nodes': [_node_name(node) for node in self._obj.nodes],
        }
        cluster_service = actor.serviceCreate(instance=self._obj.name, args=args)

        for service in producers:
            cluster_service.consume(service)

        return cluster_service

def clean_dict(d):
    for k in list(d.keys()):
        if d[k] is None:
            del d[k]
    return d


class ContainerAYS(AYSable):

    def __init__(self, storageserver):
        self._obj = storageserver
        self.actor = 'container'

    def create(self, aysrepo):
        actor = aysrepo.actorGet(self.actor)
        args = {
            'node': _node_name(self._obj.node),
            'hostname': self._obj.hostname,
            'flist': self._obj.flist,
            # 'initProcesses': ,TODO
            # 'zerotier': ,
            # 'bridges': ,
            'hostNetworking': self._obj.host_network,
            'storage': self._obj.storage,
            'id': self._obj.id,
        }

        return actor.serviceCreate(instance=self._obj.name, args=clean_dict(args))


class ARDBAys(AYSable):

    def __init__(self, storageserver):
        self._obj = storageserver
        self.actor = 'ardb'

    def create(self, aysrepo):
        actor = aysrepo.actorGet(self.actor)
        args = {
            'homeDir': "/mnt/data",
            'bind': self._obj.bind,
            'master': self._obj.master,
            'container': self._obj.name,
        }
        return actor.serviceCreate(instance=self._obj.name, args=clean_dict(args))
