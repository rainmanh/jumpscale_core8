from JumpScale import j

base = j.tools.cuisine._getBaseClass()


class CuisineArakoon(base):

    def __init__(self, executor, cuisine):
        self._executor = executor
        self._cuisine = cuisine
        self.logger = j.logger.get("j.tools.cuisine.arakoon")

    def _build(self):
        # self._cuisine.installer.base()
        exists = self._cuisine.core.command_check("arakoon")

        if exists:
            cmd = self._cuisine.core.command_location("arakoon")
            dest = "%s/arakoon" % self._cuisine.core.dir_paths["binDir"]
            if j.sal.fs.pathClean(cmd) != j.sal.fs.pathClean(dest):
                self._cuisine.core.file_copy(cmd, dest)
        else:
            dest = self._cuisine.development.git.pullRepo('https://github.com/openvstorage/arakoon.git')
            self._cuisine.core.run('cd %s && git pull && git fetch --tags && git checkout tags/1.9.7' % dest)

            opam_root = self._cuisine.core.args_replace('$tmpDir/OPAM')
            cmd = "opam config env --root=%s --dot-profile %s" % (opam_root, self._cuisine.bash.profilePath)
            _, out, _ = self._cuisine.core.run(cmd, profile=True)

            cmd = 'cd %s && eval `%s` && make' % (dest, out)
            self._cuisine.core.run(cmd, profile=True)

            self._cuisine.core.file_copy('%s/arakoon.native' % dest, "$binDir/arakoon", overwrite=True)

        self._cuisine.core.dir_ensure('$varDir/data/arakoon')

    def _install_ocaml(self):
        self.logger.info("download opam installer")
        self._cuisine.core.file_download(
            'https://raw.github.com/ocaml/opam/master/shell/opam_installer.sh', to='$tmpDir/opam_installer.sh')
        self.logger.info("install opam")
        self._cuisine.core.run('chmod +x $tmpDir/opam_installer.sh')
        ocaml_version = '4.02.3'
        cmd = 'yes | $tmpDir/opam_installer.sh $binDir %s' % ocaml_version
        self._cuisine.core.run(cmd, profile=True)

        self.logger.info("initialize opam")
        opam_root = self._cuisine.core.args_replace('$tmpDir/OPAM')
        self._cuisine.core.dir_ensure(opam_root)
        cmd = 'opam init --root=%s --comp %s -a --dot-profile %s' % (
            opam_root, ocaml_version, self._cuisine.bash.profilePath)
        self._cuisine.core.run(cmd, profile=True)

        cmd = "opam config env --root=%s --dot-profile %s" % (opam_root, self._cuisine.bash.profilePath)
        self._cuisine.core.run(cmd, profile=True)

        opam_deps = (
            'ocamlfind',
            'ssl',
            'camlbz2',
            'snappy',
            'sexplib',
            'bisect',
            'lwt.2.5.1',
            'camltc',
            'cstruct',
            'ctypes-foreign',
            'uuidm',
            'zarith',
            'mirage-no-xen.1',
            'quickcheck.1.0.2',
            'cmdliner',
            'conf-libev',
            'depext',
            'tiny_json',
            'ppx_deriving.3.1',
            'ppx_deriving_yojson',
            'core.113.00.00',
            'redis',
            'uri.1.9.1',
            'result',
            'ocplib-endian'
        )

        self.logger.info("start installation of ocaml pacakges")
        cmd = 'opam update && opam install -y {}'.format(' '.join(opam_deps))
        self._cuisine.core.run(cmd, profile=True, die=False)

    def _install_deps(self):
        # apt_deps = "curl libev-dev libssl-dev libsnappy-dev libgmp3-dev ocaml ocaml-native-compilers camlp4-extra aspcud libbz2-dev protobuf-compiler m4 pkg-config"
        apt_deps = 'curl make m4 gcc patch unzip git pkg-config libprotobuf9v5 libprotoc9v5 protobuf-compiler libsnappy-dev libssl-dev libssl-doc zlib1g-dev bzip2-doc libbz2-dev libncurses5-dev libtinfo-dev libgmp-dev libgmpxx4ldbl libev-dev libev4'
        self._cuisine.package.multiInstall(apt_deps)

    def build(self, start=True):
        self._install_deps()
        self._install_ocaml()
        self._build()
        if start:
            self.start("arakoon")

    def start(self, name="arakoon"):
        which = self._cuisine.core.command_location("arakoon")
        self._cuisine.core.dir_ensure('$varDir/data/arakoon')
        cmd = "%s --config $cfgDir/arakoon/arakoon.ini" % which
        self._cuisine.process.kill("arakoon")
        self._cuisine.processmanager.ensure("arakoon", cmd=cmd, env={}, path="")

    def create_cluster(self, id):
        return ArakoonCluster(id, self._cuisine)


class ArakoonNode(object):

    def __init__(self, ip, home, client_port, messaging_port, log_level):
        super(ArakoonNode, self).__init__()
        self.id = ''
        self.ip = ip
        self.home = j.sal.fs.pathClean(home)
        self.client_port = client_port
        self.messaging_port = messaging_port
        self.log_level = log_level


class ArakoonCluster(object):

    def __init__(self, id, cuisine):
        super(ArakoonCluster, self).__init__()
        self.id = id
        self._cuisine = cuisine
        self.plugins = []
        self.nodes = []

    def add_node(self, ip, home='$varDir/data/arakoon', client_port=7080, messaging_port=10000, log_level='info'):
        home = self._cuisine.core.args_replace(home)
        node = ArakoonNode(ip=ip, home=home, client_port=client_port,
                           messaging_port=messaging_port, log_level=log_level)
        node.id = 'node_%d' % len(self.nodes)
        self.nodes.append(node)
        return node

    def get_config(self):
        tmp = j.sal.fs.getTempFileName()
        f = j.tools.inifile.new(tmp)

        f.addSection('global')
        cluster = ''
        for node in self.nodes:
            cluster += '%s, ' % node.id
        cluster = cluster[:-2]
        f.addParam('global', 'cluster', cluster)
        f.addParam('global', 'cluster_id', self.id)
        if len(self.plugins) > 0:
            plugins = ', '.join(self.plugins)
            f.addParam('plugins', plugins)

        for node in self.nodes:
            f.addSection(node.id)
            f.addParam(node.id, 'ip', node.ip)
            f.addParam(node.id, 'client_port', node.client_port)
            f.addParam(node.id, 'messaging_port', node.messaging_port)
            f.addParam(node.id, 'home', node.home)
            f.addParam(node.id, 'log_level', node.log_level)

        f.write()
        content = j.sal.fs.fileGetContents(tmp)
        j.sal.fs.remove(tmp)
        return content


if __name__ == '__main__':
    c = j.tools.cuisine.local
    cluster = c.apps.arakoon.create_cluster('test')
    node1 = cluster.add_node('127.0.0.1')
    node2 = cluster.add_node('172.20.0.55')
    cfg = cluster.get_config()
    print(cfg)
