from JumpScale import j
from time import sleep


base = j.tools.cuisine._getBaseClass()


class CuisineAlba(base):

    def __init__(self, executor, cuisine):
        self._executor = executor
        self._cuisine = cuisine
        self.logger = j.logger.get("j.tools.cuisine.alba")

        self.arakoon_version = 'a4e7dffc08cb999e1b1de45eb7f6efe8c978eb81'
        self.alba_version = '0.9.19'
        self.ocaml_version = '4.03.0'
        self.opam_root = None

    def build(self, start=True):
        self._install_deps()
        self._build()

    def _install_deps_opam(self):
        self._cuisine.package.update()
        self._cuisine.package.upgrade(distupgrade=True)

        apt_deps = """
        build-essential m4 apt-utils libffi-dev libssl-dev libbz2-dev libgmp3-dev libev-dev libsnappy-dev \
        libxen-dev help2man pkg-config time aspcud wget rsync darcs git unzip protobuf-compiler libgcrypt20-dev \
        libjerasure-dev yasm automake python-dev python-pip debhelper psmisc strace curl g++ libgflags-dev \
        sudo libtool libboost-all-dev fuse sysstat ncurses-dev librdmacm-dev
        """
        self._cuisine.package.multiInstall(apt_deps, allow_unauthenticated=True)

        # OPAM
        self.opam_root = self._cuisine.core.args_replace('$tmpDir/OPAM')
        
        # profile fix
        if not self._cuisine.core.file_exists('/root/.profile_js'):
            self._cuisine.core.file_write('/root/.profile_js', "")

        # self._cuisine.core.run('wget https://raw.github.com/ocaml/opam/master/shell/opam_installer.sh')
        self._cuisine.core.file_download(
            'https://raw.github.com/ocaml/opam/master/shell/opam_installer.sh', to='$tmpDir/opam_installer.sh')
        self._cuisine.core.run('sed -i "/read -p/d" $tmpDir/opam_installer.sh')  # remove any confirmation
        self._cuisine.core.run('bash $tmpDir/opam_installer.sh $binDir %s' % self.ocaml_version, profile=True, shell=True)

        cmd = 'opam init --root=%s --comp %s -a --dot-profile %s' % (
            self.opam_root, self.ocaml_version, self._cuisine.bash.profilePath)
        self._cuisine.core.run(cmd, profile=True, shell=True)
        
        janestreet = self._cuisine.development.git.pullRepo('https://github.com/janestreet/opam-repository.git', depth=None, ssh=False)
        self._cuisine.core.run('cd %s && git pull && git checkout b98fd1964856f0c0b022a42ec4e6fc6c7bad2e81' % janestreet, shell=True)
        self._cuisine.core.run("opam repo --root=%s -k local add janestreet %s || exit 0" % (self.opam_root, janestreet), profile=True)

        cmd = "opam config env --root=%s --dot-profile %s > $tmpDir/opam.env" % (
            self.opam_root, self._cuisine.bash.profilePath)
        self._cuisine.core.run(cmd, die=False, profile=True, shell=True)

        opam_deps = """oasis.0.4.6 ocamlfind ssl.0.5.2 camlbz2 snappy sexplib bisect lwt.2.5.2 \
        camltc.0.9.3 ocplib-endian.1.0 cstruct ctypes ctypes-foreign uuidm zarith mirage-no-xen.1 \
        quickcheck.1.0.2 cmdliner conf-libev depext kinetic-client tiny_json ppx_deriving \
        ppx_deriving_yojson core.114.05+21 redis.0.3.1 uri.1.9.2 result
        """

        self._cuisine.core.execute_bash(
            'source $tmpDir/opam.env && opam update && opam install -y %s' % opam_deps, profile=True)

    def _install_deps_intel_storage(self):
        url = 'https://01.org/sites/default/files/downloads/intelr-storage-acceleration-library-open-source-version/isa-l-2.14.0.tar.gz'
        self._cuisine.core.file_download(url, to='$tmpDir/isa-l-2.14.0.tar.gz')

        self._cuisine.core.run('cd $tmpDir && tar xfzv isa-l-2.14.0.tar.gz')
        self._cuisine.core.run('cd $tmpDir/isa-l-2.14.0 && ./autogen.sh && ./configure')
        self._cuisine.core.run('cd $tmpDir/isa-l-2.14.0 && make && make install')

        """
        RUN wget https://01.org/sites/default/files/downloads/intelr-storage-acceleration-library-open-source-version/isa-l-2.14.0.tar.gz
        RUN tar xfzv isa-l-2.14.0.tar.gz
        RUN cd isa-l-2.14.0 && ./autogen.sh && ./configure
        RUN cd isa-l-2.14.0 && make
        RUN cd isa-l-2.14.0 && make install
        """
        return

    def _install_deps_cpp(self):
        self._cuisine.package.multiInstall("libgtest-dev cmake", allow_unauthenticated=True)
        self._cuisine.core.run('cd /usr/src/gtest && cmake . && make && mv libg* /usr/lib/')

        """
        RUN apt-get update && apt-get -y install libgtest-dev cmake
        RUN cd /usr/src/gtest \
            && cmake . \
            && make \
            && mv libg* /usr/lib/
        """

        return

    def _install_deps_arakoon(self):
        aradest = self._cuisine.development.git.pullRepo(
            'https://github.com/openvstorage/arakoon.git', branch="1.9", depth=None, ssh=False)
        pfx = 'cd %s && source $tmpDir/opam.env' % aradest

        self._cuisine.core.run('%s && git pull && git checkout %s' % (pfx, self.arakoon_version), shell=True)
        self._cuisine.core.run('%s && make' % pfx, shell=True)
        
        if self._cuisine.core.file_exists('$tmpDir/OPAM/4.03.0/lib/arakoon_client/META'):
            self._cuisine.core.file_unlink('$tmpDir/OPAM/4.03.0/lib/arakoon_client/META')

        prefix = '%s/%s' % (self.opam_root, self.ocaml_version)
        libdir = 'ocamlfind printconf destdir'
        cmd = '%s && export PREFIX=%s && export OCAML_LIBDIR=$(%s) && make install' % (pfx, prefix, libdir)

        self._cuisine.core.execute_bash(cmd, profile=True)
        self._cuisine.core.file_copy(j.sal.fs.joinPaths(aradest, 'arakoon.native'), "$binDir/arakoon")

        """
        RUN git clone https://github.com/openvstorage/arakoon.git
        RUN cd arakoon && git pull && git checkout tags/1.9.3
        RUN cd arakoon && eval `${opam_env}` && make
        RUN cd arakoon && eval `${opam_env}` \
            && export PREFIX=${opam_root}/${ocaml_version} \
            && export OCAML_LIBDIR=`ocamlfind printconf destdir` \
            && make install
        """
        return

    def _install_deps_orocksdb(self):
        #
        # cleaning
        #
        if self._cuisine.core.file_exists('$tmpDir/OPAM/%s/lib/rocks/META' % self.ocaml_version):
            print('rocksdb already found')
            return
        
        if self._cuisine.core.file_exists('/usr/local/lib/librocksdb.so'):
            self._cuisine.core.run('rm -rfv /usr/local/lib/librocksdb.*')
        
        if self._cuisine.core.dir_exists('/opt/code/github/domsj/orocksdb'):
            self._cuisine.core.dir_remove('/opt/code/github/domsj/orocksdb', True)

        #
        # install
        #
        commit = '26c45963f1f305825785592efb41b50192a07491'
        orodest = self._cuisine.development.git.pullRepo('https://github.com/domsj/orocksdb.git', depth=None, ssh=False)
        
        pfx = 'cd %s && source $tmpDir/opam.env' % orodest
        self._cuisine.core.run('%s && git pull && git checkout %s' % (pfx, commit))

        self._cuisine.core.run('%s && ./install_rocksdb.sh && make build install' % pfx)

        """
        RUN git clone https://github.com/domsj/orocksdb.git \
            && eval `${opam_env}` \
            && cd orocksdb \
            && git checkout 8bc61d8a451a2724399247abf76643aa7b2a07e9 \
            && ./install_rocksdb.sh \
            && make build install
        """
        return
    
    def _install_deps_sources(self):
        self._cuisine.core.file_write('/etc/apt/sources.list.d/wily-universe.list', "deb http://archive.ubuntu.com/ubuntu/ wily universe\n")
        self._cuisine.core.file_write('/etc/apt/sources.list.d/ovsaptrepo.list', "deb http://apt.openvstorage.org unstable main\n")
        self._cuisine.package.update()
        
        apt_deps = """
        librdmacm-dev clang-3.5 liblttng-ust0 librdmacm1 libtokyocabinet9 libstdc++6:amd64 libzmq3 \
        librabbitmq1 libomnithread3c2 libomniorb4-1 libhiredis0.13 liblz4-1 libxio-dev libxio0 \
        omniorb-nameserver libunwind8-dev libaio1 libaio1-dbg libaio-dev libz-dev libbz2-dev \
        libgoogle-glog-dev libibverbs-dev"""
        
        self._cuisine.package.multiInstall(apt_deps, allow_unauthenticated=True)
        
    def _install_deps_ordma(self):
        #
        # cleaning
        #
        if self._cuisine.core.file_exists('$tmpDir/OPAM/%s/lib/ordma/META' % self.ocaml_version):
            print('ordma already found')
            return
        
        #
        # install
        #
        commit = 'tags/0.0.2'
        ordmadest = self._cuisine.development.git.pullRepo('https://github.com/toolslive/ordma.git', depth=None, ssh=False)
        
        self._cuisine.core.run('cd %s && git pull && git fetch --tags && git checkout %s' % (ordmadest, commit))
        
        pfx = 'cd %s && source $tmpDir/opam.env' % ordmadest
        self._cuisine.core.run('%s && eval `${opam_env}` && make install' % pfx)
        
        """
        RUN git clone https://github.com/toolslive/ordma.git \
            && cd ordma \
            && git checkout tags/0.0.2 \
            && eval `${opam_env}` \
            && make install
        """
        pass

    def _install_deps_gobjfs(self):
        commit = '3b591baf7518987ce1b6c828865f0089007281e4'
        gobjfsdest = self._cuisine.development.git.pullRepo('https://github.com/openvstorage/gobjfs.git', depth=None, ssh=False)
        
        self._cuisine.core.run('cd %s && git pull && git fetch --tags && git checkout %s' % (gobjfsdest, commit))
        self._cuisine.core.run('cd %s && mkdir -p build && cd build && cmake -DCMAKE_BUILD_TYPE=RELWITHDEBINFO ..' % gobjfsdest)
        self._cuisine.core.run('cd %s/build && make && make install' % gobjfsdest)
        
        """
        RUN git clone https://github.com/openvstorage/gobjfs.git
        RUN cd gobjfs  && git pull && git checkout 3b591baf7518987ce1b6c828865f0089007281e4
        RUN cd gobjfs \
               && mkdir build \
               && cd build \
               && cmake -DCMAKE_BUILD_TYPE=RELWITHDEBINFO .. \
               && make \
               && make install
        """
        pass

    def _install_deps_etcd(self):
        url = 'https://github.com/coreos/etcd/releases/download/v2.2.4/etcd-v2.2.4-linux-amd64.tar.gz'
        self._cuisine.core.file_download(url, to='$tmpDir/etcd-v2.2.4-linux-amd64.tar.gz')

        self._cuisine.core.run('cd $tmpDir && tar xfzv etcd-v2.2.4-linux-amd64.tar.gz')
        self._cuisine.core.run('cp $tmpDir/etcd-v2.2.4-linux-amd64/etcd /usr/bin')
        self._cuisine.core.run('cp $tmpDir/etcd-v2.2.4-linux-amd64/etcdctl /usr/bin')

        """
        RUN curl -L  https://github.com/coreos/etcd/releases/download/v2.2.4/etcd-v2.2.4-linux-amd64.tar.gz -o etcd-v2.2.4-linux-amd64.tar.gz
        RUN tar xzvf etcd-v2.2.4-linux-amd64.tar.gz
        RUN cp ./etcd-v2.2.4-linux-amd64/etcd /usr/bin \
            && cp ./etcd-v2.2.4-linux-amd64/etcdctl /usr/bin
        """

        return

    def _install_deps(self):
        self._install_deps_opam()
        self._install_deps_intel_storage()
        self._install_deps_cpp()
        self._install_deps_arakoon()
        self._install_deps_orocksdb()
        self._install_deps_sources()
        self._install_deps_ordma()
        self._install_deps_gobjfs()
        self._install_deps_etcd()

    def _build(self):
        repo = self._cuisine.development.git.pullRepo('https://github.com/openvstorage/alba', depth=None, ssh=False)
        
        self._cuisine.core.run('cd %s && git checkout %s' % (repo, self.alba_version))

        self._cuisine.core.execute_bash('source $tmpDir/opam.env && cd %s; make' % repo, profile=True)
        self._cuisine.core.file_copy('%s/ocaml/alba.native' % repo, '$binDir/alba')
        self._cuisine.core.file_copy('%s/ocaml/albamgr_plugin.cmxs' % repo, '$binDir/albamgr_plugin.cmxs')
        self._cuisine.core.file_copy('%s/ocaml/nsm_host_plugin.cmxs' % repo, '$binDir/nsm_host_plugin.cmxs')
        self._cuisine.core.file_copy('%s/ocaml/disk_failure_tests.native' % repo, '$binDir/disk_failure_tests.native')
