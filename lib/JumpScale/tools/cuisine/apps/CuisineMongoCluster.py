from JumpScale import j
from time import sleep


class Startable:

    def __init__(self):
        self.installed = False
        self.started = False

    def _install(self):
        self.installed = True

    def _start(self):
        self.started = True

    def install(self, *args, **kwargs):
        if not self.installed:
            return self._install()
        else:
            return False

    def start(self, *args, **kwargs):
        if not self.started:
            return self._start()
        else:
            return False

    @staticmethod
    def ensure_started(fn):
        def fn2(self, *args, **kwargs):
            if not self.started:
                self.start()
            return fn(self, *args, **kwargs)
        return fn2

    @staticmethod
    def ensure_installed(fn):
        def fn2(self, *args, **kwargs):
            if not self.installed:
                self.install()
            return fn(self, *args, **kwargs)
        return fn2


class MongoInstance(Startable):

    def __init__(self, cuisine, addr=None, private_port=27021, public_port=None, type_="shard", replica='', configdb='', dbdir=None):
        super().__init__()
        self._cuisine = cuisine
        if not addr:
            self.addr = cuisine.core.executor.addr
        else:
            self.addr = addr
        self.private_port = private_port
        self.public_port = public_port
        self.type_ = type_
        self.replica = replica
        self.configdb = configdb
        if dbdir is None:
            dbdir = "$varDir/data/db"
        if public_port is None:
            public_port = private_port
        self.dbdir = dbdir
        print(cuisine, private_port, public_port, type_, replica, configdb, dbdir)

    def _install(self):
        super()._install()
        self._cuisine.core.dir_ensure(self.dbdir)
        return self._cuisine.apps.mongodb.build(start=False)

    def _gen_service_name(self):
        name = "ourmongos" if self.type_ == "mongos" else "ourmongod"
        if self.type_ == "cfg":
            name += "_cfg"
        return name

    def _gen_service_cmd(self):
        cmd = "mongos" if self.type_ == "mongos" else "mongod"
        args = ""
        if self.type_ == "cfg":
            args += " --configsvr"
        if self.type_ != "mongos":
            args += " --dbpath %s" % (self.dbdir)
        if self.private_port:
            args += " --port %s" % (self.private_port)
        if self.replica:
            args += " --replSet %s" % (self.replica)
        if self.configdb:
            args += " --configdb %s" % (self.configdb)
        return '$binDir/' + cmd + args

    @Startable.ensure_installed
    def _start(self):
        super()._start()
        print("starting: ", self._gen_service_name(), self._gen_service_cmd())
        a = self._cuisine.processmanager.ensure(self._gen_service_name(), self._gen_service_cmd())
        return a

    @Startable.ensure_started
    def execute(self, cmd):
        for i in range(5):
            rc, out, err = self._cuisine.core.run("LC_ALL=C $binDir/mongo --port %s --eval '%s'" %
                                                 (self.private_port, cmd.replace("\\", "\\\\").replace("'", "\\'")), die=False)
            if not rc and out.find('errmsg') == -1:
                print('command executed %s' % (cmd))
                break
            sleep(5)
        else:
            print('cannot execute command %s' % (cmd))
        return rc, out

    def __repr__(self):
        return "%s:%s" % (self.addr, self.public_port)

    __str__ = __repr__


class MongoSInstance(Startable):

    def __init__(self, nodes, configdb):
        super().__init__()
        self.nodes = nodes
        self.configdb = configdb
        for i in nodes:
            i.configdb = configdb
            i.type_ = "mongos"

    @Startable.ensure_installed
    def _start(self):
        super()._start()
        self.configdb.start()
        [i.start() for i in self.nodes]

    @Startable.ensure_started
    def add_shard(self, replica):
        self.nodes[0].execute("sh.addShard( \"%s\" )" % (replica))

    def add_shards(self, replicas):
        return [self.add_shard(i) for i in replicas]


class MongoCluster(Startable):

    def __init__(self, nodes, configdb, shards, unique=""):
        super().__init__()
        self.nodes = nodes
        self.configdb = configdb
        self.shards = shards
        self.unique = unique
        self.mongos = MongoSInstance(nodes, configdb)

    def add_shards(self):
        self.mongos.add_shards(self.shards)

    def _install(self):
        super()._install()
        [i.install() for i in self.shards]
        self.mongos.start()
        self.add_shards()

    @Startable.ensure_installed
    def _start(self):
        super()._start()
        self.mongos.start()
        [i.start() for i in self.shards]


class MongoReplica(Startable):

    def __init__(self, nodes, primary=None, name="", configsvr=False):
        super().__init__()
        if not primary:
            primary = nodes[0]
            nodes = nodes[1:]

        self.name = name
        self.configsvr = configsvr
        self.primary = primary
        self.nodes = nodes
        self.all = [primary] + nodes

        for i in self.all:
            i.replica = name
            if configsvr:
                i.type_ = "cfg"

    def _prepare_json_all(self):
        reprs = [repr(i) for i in self.all]
        return ", ".join(["{ _id: %s, host: \"%s\" , priority: %f}" % (i, k, 1.0 / i) for i, k in enumerate(reprs)])

    def _prepare_init(self):
        cfg = "configsvr: true,version:1," if self.configsvr else ""
        return """rs.initiate( {_id: "%s",%smembers: [%s]} )""" % (self.name, cfg, self._prepare_json_all())

    def _install(self):
        super()._install()
        self.start()
        self.primary.execute(self._prepare_init())

    @Startable.ensure_installed
    def _start(self):
        super()._start()
        for i in self.all:
            i.start()

    def __repr__(self):
        return "%s/%s" % (self.name, self.primary)

    __str__ = __repr__


class MongoConfigSvr(Startable):

    def __init__(self, nodes, primary=None, name=""):
        super().__init__()
        self.name = name
        self.rep = MongoReplica(nodes, primary, name=self.name, configsvr=True)

    @Startable.ensure_installed
    def _start(self):
        super()._start()
        self.rep.start()

    def __repr__(self):
        return self.rep.__repr__()

    __str__ = __repr__


def mongoCluster(shards_nodes, config_nodes, mongos_nodes, shards_replica_set_counts=1, unique=""):
    args = []
    for i in [shards_nodes, config_nodes, mongos_nodes]:
        cuisines = []
        for k in i:
            cuisines.append(MongoInstance(j.tools.cuisine.get(k['executor']), addr=k.get('addr', None), private_port=k['private_port'],
                                          public_port=k.get('public_port'), dbdir=k.get('dbdir')))
        args.append(cuisines)
    return _mongoCluster(args[0], args[1], args[2], shards_replica_set_counts=shards_replica_set_counts, unique=unique)


def _mongoCluster(shards_css, config_css, mongos_css, shards_replica_set_counts=1, unique=""):
    shards_replicas = [shards_css[i:i + shards_replica_set_counts]
                       for i in range(0, len(shards_css), shards_replica_set_counts)]
    shards = [MongoReplica(i, name="%s_sh_%d" % (unique, num)) for num, i in enumerate(shards_replicas)]
    cfg = MongoConfigSvr(config_css, name="%s_cfg" % (unique))
    cluster = MongoCluster(mongos_css, cfg, shards)
    cluster.install()
    cluster.start()
    return cluster


if __name__ == "__main__":
    mongoCluster(
        [{
            "executor": j.tools.executor.getSSHBased(addr="10.0.3.194", port=22, login="root", passwd="rooter"),
            "public_port": 27025,
            "private_port": 27025,
            "dbdir": "$varDir/db2/data"
        }, {
            "executor": j.tools.executor.getSSHBased(addr="10.0.3.112", port=22, login="root", passwd="rooter"),
            "public_port": 27025,
            "private_port": 27025,
            "dbdir": "$varDir/db2/data"
        }, {
            "executor": j.tools.executor.getSSHBased(addr="10.0.3.126", port=22, login="root", passwd="rooter"),
            "public_port": 27025,
            "private_port": 27025,
            "dbdir": "$varDir/db2/data"
        }, {
            "executor": j.tools.executor.getSSHBased(addr="10.0.3.209", port=22, login="root", passwd="rooter"),
            "public_port": 27025,
            "private_port": 27025,
            "dbdir": "$varDir/db2/data"
        }],
        [{
            "executor": j.tools.executor.getSSHBased(addr="10.0.3.205", port=22, login="root", passwd="rooter"),
            "public_port": 27025,
            "private_port": 27025,
            "dbdir": "$varDir/db2/data"
        }, {
            "executor": j.tools.executor.getSSHBased(addr="10.0.3.204", port=22, login="root", passwd="rooter"),
            "public_port": 27025,
            "private_port": 27025,
            "dbdir": "$varDir/db2/data"
        }],
        [{
            "executor": j.tools.executor.getSSHBased(addr="10.0.3.119", port=22, login="root", passwd="rooter"),
            "public_port": 27025,
            "private_port": 27025,
            "dbdir": "$varDir/db2/data"
        }, {
            "executor": j.tools.executor.getSSHBased(addr="10.0.3.79", port=22, login="root", passwd="rooter"),
            "public_port": 27025,
            "private_port": 27025,
            "dbdir": "$varDir/db2/data"
        }], 2)
