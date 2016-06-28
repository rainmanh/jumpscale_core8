from JumpScale import j
from time import sleep


from ActionDecorator import ActionDecorator


"""
please ensure that the start and build methods are separate and
the build doesnt place anyfile outside opt as it will be used in aysfs mounted system
"""


class actionrun(ActionDecorator):

    def __init__(self, *args, **kwargs):
        ActionDecorator.__init__(self, *args, **kwargs)
        self.selfobjCode = "cuisine=j.tools.cuisine.getFromId('$id');selfobj=cuisine.apps.arakoon"


class Arakoon:

    def __init__(self, executor, cuisine):
        self.executor = executor
        self.cuisine = cuisine
        self.logger = j.logger.get("j.tools.cuisine.arakoon")

    @actionrun(action=True)
    def _build(self):
        self.cuisine.installer.base()
        exists = self.cuisine.core.command_check("arakoon")

        if exists:
            cmd = self.cuisine.core.command_location("arakoon")
            dest = "%s/arakoon" % self.cuisine.core.dir_paths["binDir"]
            if j.sal.fs.pathClean(cmd) != j.sal.fs.pathClean(dest):
                self.cuisine.core.file_copy(cmd, dest)
        else:
            dest = self.cuisine.git.pullRepo('https://github.com/openvstorage/arakoon.git')
            self.cuisine.core.run('cd %s && git pull && git checkout tags/1.9.7' % dest)

            opam_root = self.cuisine.core.args_replace('$tmpDir/OPAM')
            cmd = "$opam config env --root=%s --dot-profile %s" % (opam_root, self.cuisine.bash.profilePath)
            rc, opam_env = self.cuisine.core.run(cmd, die=False, profile=True)

            cmd = 'cd %s && eval `%s` && make' % (dest, opam_env)
            self.cuisine.core.run_script(cmd, profile=True)

            self.cuisine.core.file_copy('%s/arakoon.native' % dest, "$binDir/arakoon", overwrite=True)

        self.cuisine.core.dir_ensure('$varDir/data/arakoon')

    def _install_ocaml(self):
        self.logger.info("download opam installer")
        self.cuisine.core.file_download('https://raw.github.com/ocaml/opam/master/shell/opam_installer.sh', to='$tmpDir/opam_installer.sh')
        self.logger.info("install opam")
        self.cuisine.core.run('chmod +x $tmpDir/opam_installer.sh')
        ocaml_version = '4.02.3'
        cmd = '$tmpDir/opam_installer.sh $binDir %s' % ocaml_version
        self.cuisine.core.run(cmd, profile=True)

        self.logger.info("initialize opam")
        opam_root = self.cuisine.core.args_replace('$tmpDir/OPAM')
        self.cuisine.core.dir_ensure(opam_root)
        cmd = 'opam init --root=%s --comp %s -a --dot-profile %s' % (opam_root, ocaml_version, self.cuisine.bash.profilePath)
        self.cuisine.core.run(cmd, profile=True)

        cmd = "opam config env --root=%s --dot-profile %s" % (opam_root, self.cuisine.bash.profilePath)
        rc, opam_env = self.cuisine.core.run(cmd, die=False, profile=True)

        self.logger.info("start installation of ocaml pacakges")
        cmd="""eval `%s` && \
    opam update && \
    opam install -y -q \
        ocamlfind \
        ssl.0.5.2 \
        camlbz2 \
        snappy \
        sexplib \
        bisect \
        lwt.2.5.1 \
        camltc \
        cstruct \
        ctypes \
        ctypes-foreign \
        uuidm \
        zarith \
        mirage-no-xen.1 \
        quickcheck.1.0.2 \
        cmdliner \
        conf-libev \
        depext \
        kinetic-client \
        tiny_json \
        ppx_deriving.3.1 \
        ppx_deriving_yojson \
        core.113.00.00 \
        redis \
        uri.1.9.1 \
        result""" % opam_env
        self.cuisine.core.run_script(cmd, profile=True)

    def _install_deps(self):
        apt_deps = "libev-dev libssl-dev libsnappy-dev libgmp3-dev ocaml ocaml-native-compilers camlp4-extra opam aspcud libbz2-dev protobuf-compiler m4 pkg-config"
        self.cuisine.package.multiInstall(apt_deps)

    def build(self, start=True):
        self._install_deps()
        self._install_ocaml()
        self._build()
        if start:
            self.start("arakoon")

    def start(self, name="arakoon"):
        which = self.cuisine.core.command_location("arakoon")
        self.cuisine.core.dir_ensure('$varDir/data/arakoon')
        cmd = "%s --config $cfgDir/arakoon/arakoon.ini" % which
        self.cuisine.process.kill("arakoon")
        self.cuisine.processmanager.ensure("arakoon", cmd=cmd, env={}, path="")

    def create_cluster(self, id):
        return ArakoonCluster(id, self.cuisine)


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
        self.cuisine = cuisine
        self.nodes = []

    def add_node(self, ip, home='$varDir/data/arakoon', client_port=7080, messaging_port=10000, log_level='info'):
        home = self.cuisine.core.args_replace(home)
        node = ArakoonNode(ip=ip, home=home, client_port=client_port, messaging_port=messaging_port, log_level=log_level)
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

        for node in self.nodes:
            f.addSection(node.id)
            f.addParam(node.id, 'ip', node.ip)
            f.addParam(node.id, 'client_port', node.client_port)
            f.addParam(node.id, 'messaging_port', node.messaging_port)
            f.addParam(node.id, 'home', node.home)
            f.addParam(node.id, 'log_level', node.log_level)

        f.write()
        return j.sal.fs.fileGetContents(tmp)


if __name__ == '__main__':
    c = j.tools.cuisine.local
    cluster = c.apps.arakoon.create_cluster('test')
    node1 = cluster.add_node('127.0.0.1')
    node2 = cluster.add_node('172.20.0.55')
    cfg = cluster.get_config()
    print(cfg)
