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
        self.selfobjCode = "cuisine=j.tools.cuisine.getFromId('$id');selfobj=cuisine.apps.volumedriver"

base=j.tools.cuisine.getBaseClass()
class VolumeDriver(base):

    def __init__(self, executor, cuisine):
        self.executor = executor
        self.cuisine = cuisine
        self.logger = j.logger.get("j.tools.cuisine.volumedriver")

    @actionrun(action=True)
    def build(self, start=True):
        self._install_deps()
        self._build()

    @actionrun()
    def _install_deps(self):
        self.cuisine.core.file_write('/etc/apt/sources.list.d/ovsaptrepo.list', 'deb http://apt.openvstorage.org unstable main')
        self.cuisine.package.update()
        self.cuisine.package.upgrade(distupgrade=True)

        apt_deps = """
        gcc g++ clang-3.8 valgrind \
        libboost1.58-all-dev \
        build-essential sudo \
        flex bison gawk check pkg-config \
        autoconf libtool realpath bc gettext lcov \
        unzip doxygen dkms debhelper pylint git cmake \
        wget libssl-dev libpython2.7-dev libxml2-dev \
        libcurl4-openssl-dev libc6-dbg liblz4-dev \
        librabbitmq-dev libaio-dev libkrb5-dev libc-ares-dev \
        pkg-create-dbgsym elfutils \
        libloki-dev libprotobuf-dev liblttng-ust-dev libzmq3-dev \
        libtokyocabinet-dev libbz2-dev protobuf-compiler \
        libgflags-dev libsnappy-dev \
        redis-server libhiredis-dev libhiredis-dbg \
        libomniorb4-dev omniidl omniidl-python omniorb-nameserver \
        librdmacm-dev libibverbs-dev python-nose fuse \
        python-protobuf \
        supervisor rpcbind \
        libxio0 libxio-dev libev4
        """
        self.cuisine.package.multiInstall(apt_deps, allow_unauthenticated=True)

    @actionrun()
    def _build(self, version='6.0.0'):
        workspace = self.cuisine.core.args_replace("$tmpDir/volumedriver-workspace")
        self.cuisine.core.dir_ensure(workspace)

        str_repl = {
            'workspace': workspace,
            'version': version,
        }

        str_repl['volumedriver'] = self.cuisine.git.pullRepo('https://github.com/openvstorage/volumedriver', depth=None)
        str_repl['buildtools'] = self.cuisine.git.pullRepo('https://github.com/openvstorage/volumedriver-buildtools', depth=None)
        self.cuisine.core.run('cd %(volumedriver)s;git checkout tags/%(version)s' % str_repl)

        self.cuisine.core.file_link(str_repl['buildtools'], j.sal.fs.joinPaths(workspace, 'volumedriver-buildtools'))
        self.cuisine.core.file_link(str_repl['volumedriver'], j.sal.fs.joinPaths(workspace, 'volumedriver'))
        
        build_script = """
        export WORKSPACE=%(workspace)s
        export RUN_TESTS=no


        cd ${WORKSPACE}/volumedriver-buildtools/src/release/
        ./build-jenkins.sh

        cd ${WORKSPACE}
        ./volumedriver/src/buildscripts/jenkins-release-dev.sh ${WORKSPACE}/volumedriver
        """ % str_repl
        
        self.cuisine.core.run_script(build_script)
        self.cuisine.core.file_copy('$tmpDir/volumedriver-workspace/volumedriver/build/bin/*', '$binDir')
