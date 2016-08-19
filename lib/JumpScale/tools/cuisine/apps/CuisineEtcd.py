from JumpScale import j


from ActionDecorator import ActionDecorator


"""
please ensure that the start and build methods are separate and
the build doesnt place anyfile outside opt as it will be used in aysfs mounted system
"""


class actionrun(ActionDecorator):

    def __init__(self, *args, **kwargs):
        ActionDecorator.__init__(self, *args, **kwargs)
        self.selfobjCode = "cuisine=j.tools.cuisine.getFromId('$id');selfobj=cuisine.apps.etcd"

base = j.tools.cuisine.getBaseClass()


class Etcd(base):

    @actionrun(action=True)
    def build(self, start=True, host=None, peers=[]):
        """
        Build and start etcd

        @start, bool start etcd after buildinf or not
        @host, string. host of this node in the cluster e.g: http://etcd1.com
        @peer, list of string, list of all node in the cluster. [http://etcd1.com, http://etcd2.com, http://etcd3.com]
        """
        # self.cuisine.golang.install()
        C = """
        set -ex
        ORG_PATH="github.com/coreos"
        REPO_PATH="${ORG_PATH}/etcd"

        go get -x -d -u github.com/coreos/etcd

        cd $goDir/src/$REPO_PATH

        # first checkout master to prevent error if already in detached mode
        git checkout master
        # TODO: this version ot etcd doesn't build correctly
        # fallback to master for now.
        # git checkout v3.0.1

        go get -d .

        CGO_ENABLED=0 go build $GO_BUILD_FLAGS -installsuffix cgo -ldflags "-s -X ${REPO_PATH}/cmd/vendor/${REPO_PATH}/version.GitSHA=${GIT_SHA}" -o $binDir/etcd ${REPO_PATH}/cmd
        CGO_ENABLED=0 go build $GO_BUILD_FLAGS -installsuffix cgo -ldflags "-s" -o $binDir/etcdctl ${REPO_PATH}/cmd/etcdctl
        """

        C = self.cuisine.bash.replaceEnvironInText(C)
        self.cuisine.core.run_script(C, profile=True, action=True)
        self.cuisine.bash.addPath("$base/bin")

        if start:
            self.start(host, peers)

    def start(self, host=None, peers=None):
        self.cuisine.process.kill("etcd")
        if host and peers:
            cmd = self._etcd_cluster_cmd(host, peers)
        else:
            cmd = '$binDir/etcd'
        self.cuisine.processmanager.ensure("etcd", cmd)

    def _etcd_cluster_cmd(self, host, peers=[]):
        """
        return the command to execute to launch etcd as a static cluster
        @host, string. host of this node in the cluster e.g: http://etcd1.com
        @peer, list of string, list of all node in the cluster. [http://etcd1.com, http://etcd2.com, http://etcd3.com]
        """
        if host not in peers:
            peers.append(host)

        cluster = ""
        number = None
        for i, peer in enumerate(peers):
            cluster += 'infra{i}={host}:2380,'.format(i=i, host=peer)
            if peer == host:
                number = i
        cluster = cluster.rstrip(",")

        host = host.lstrip("http://").lstrip('https://')
        cmd = """$binDir/etcd -name infra{i} -initial-advertise-peer-urls http://{host}:2380 \
      -listen-peer-urls http://{host}:2380 \
      -listen-client-urls http://{host}:2379,http://127.0.0.1:2379,http://{host}:4001,http://127.0.0.1:4001 \
      -advertise-client-urls http://{host}:2379,http://{host}:4001 \
      -initial-cluster-token etcd-cluster-1 \
      -initial-cluster {cluster} \
      -initial-cluster-state new \
    """.format(host=host, cluster=cluster, i=number)
        return self.cuisine.core.args_replace(cmd)
