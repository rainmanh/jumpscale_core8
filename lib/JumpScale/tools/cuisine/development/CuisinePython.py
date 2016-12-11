from JumpScale import j

base = j.tools.cuisine._getBaseClass()


class CuisinePython(base):

    def __init__(self, executor, cuisine):
        self._executor = executor
        self._cuisine = cuisine

    def checkOpenSSL(self, reset=False):
        """
        this makes sure we also compile openssl
        """

        ldir = "$tmpDir/build/openssl"
        ldir = self._cuisine.core.args_replace(ldir)

        if not self._cuisine.core.dir_exists(ldir) or reset:
            self._cuisine.development.openssl.build(reset=reset)

        return ldir

    def build(self, destpath="", reset=False):
        """
        @param destpath, if '' then will be $tmpDir/build/python
        """

        self.checkOpenSSL(reset=reset)

        if destpath == "":
            destpath = "$tmpDir/build/python/"
        destpath = self._cuisine.core.args_replace(destpath)

        if reset:
            self._cuisine.core.run("rm -rf %s" % destpath)

        if self._cuisine.core.isMac:
            self._cuisine.core.run("xcode-select --install", die=False, showout=True)
            C = """
            openssl
            xz
            """
            # self._cuisine.package.multiInstall(C)

        # elif self._cuisine.core.isUbuntu:
        #     self._cuisine.core.run("apt-get build-dep python3.5 -f", die=False, showout=True)

        cpath = self._cuisine.development.mercurial.pullRepo("https://hg.python.org/cpython", reset=reset)
        self._cuisine.core.run("set -ex;cd %s;hg update 3.6" % cpath)

        if self._cuisine.core.isMac:
            _, opensslpath, _ = self._cuisine.core.run("brew --prefix openssl")

            openssldir = self.checkOpenSSL()
            openSSlIncludeLine = ":%s:%s/include" % (openssldir, openssldir)
            C = 'cd %s;CPPFLAGS="-I%s/include";LDFLAGS="-L%s";./configure' % (cpath, openssldir, openssldir)
        else:
            openSSl = ""
            C = "cd %s;./configure" % cpath

        print("configure python3")
        print(C)
        self._cuisine.core.file_write("%s/myconfigure.sh" % cpath, C, replaceArgs=True)

        C = "cd %s;sh myconfigure.sh" % cpath
        self._cuisine.core.run(C)

        C = "cd %s;make -s -j4" % cpath
        print("compile python3")
        print(C)
        self._cuisine.core.run(C)

        # find buildpath for lib (depending source it can be other destination)
        libBuildName = [item for item in self._cuisine.core.run(
            "ls %s/build" % cpath)[1].split("\n") if item.startswith("lib")][0]
        lpath = j.sal.fs.joinPaths(cpath, "build", libBuildName)

        self._cuisine.core.copyTree(source=lpath, dest=destpath, keepsymlinks=False, deletefirst=False,
                                    overwriteFiles=True,
                                    recursive=True, rsyncdelete=True, createdir=True)

        ignoredir = ["test", "tkinter", "turtledemo",
                     "msilib", "pydoc*", "lib2to3", "idlelib"]
        lpath = j.sal.fs.joinPaths(cpath, "lib",)
        ldest = "%s/lib" % destpath
        self._cuisine.core.copyTree(source=lpath, dest=ldest, keepsymlinks=False, deletefirst=False,
                                    overwriteFiles=True, ignoredir=ignoredir,
                                    recursive=True, rsyncdelete=True, createdir=True)

        self._cuisine.core.file_copy("%s/python.exe" % cpath, "%s/python3" % destpath)

        # copy includes
        lpath = j.sal.fs.joinPaths(cpath, "Include",)
        ldest = j.sal.fs.joinPaths(destpath, "include")
        self._cuisine.core.copyTree(source=lpath, dest=ldest, keepsymlinks=False, deletefirst=False,
                                    overwriteFiles=True, ignoredir=ignoredir,
                                    recursive=True, rsyncdelete=True, createdir=True)

        C = """

        export JSBASE=`pwd`


        export PATH=$JSBASE/bin:$JSPATH:/usr/local/bin:/usr/bin:/bin

        #export LUA_PATH="/opt/jumpscale8/lib/lua/?.lua;./?.lua;/opt/jumpscale8/lib/lua/?/?.lua;/opt/jumpscale8/lib/lua/tarantool/?.lua;/opt/jumpscale8/lib/lua/?/init.lua"


        export PYTHONPATH=$JSBASE:$JSBASE/lib:$JSBASE/lib/site-packages
        export PYTHONHOME=$JSBASE
        export CPATH=$cpath/Include:$cpath$openssl

        export LC_ALL=en_US.UTF-8
        export LANG=en_US.UTF-8

        export LD_LIBRARY_PATH=$JSBASE/bin
        export PS1="JS8: "
        if [ -n "$BASH" -o -n "$ZSH_VERSION" ] ; then
                hash -r 2>/dev/null
        fi
        """
        C = C.replace("$cpath", cpath)

        # these are libraries on system specificly for openssl
        C = C.replace("$openssl", openSSlIncludeLine)

        self._cuisine.core.file_write("%s/env.sh" % destpath, C, replaceArgs=True)

        C = """
        set -ex
        cd %s
        source env.sh
        rm -rf get-pip.py
        curl https://bootstrap.pypa.io/get-pip.py > get-pip.py
        python3 get-pip.py
        """ % destpath
        self._cuisine.core.run(C)

        msg = "to test do:\ncd %s;source env.sh;python3" % destpath
        msg = self._cuisine.core.args_replace(msg)
        print(msg)
        return destpath

    def sandbox(self, build=True, reset=False, destpath=""):
        if destpath == "":
            destpath = "$tmpDir/build/python/"
        destpath = self._cuisine.core.args_replace(destpath)
        if build:
            self.build(destpath, reset)
        # needs at least /JS8/code/github/jumpscale/jumpscale_core8/install/dependencies.py
        C = """
        uvloop
        redis
        paramiko
        watchdog
        gitpython
        click
        pymux
        uvloop
        pyyaml
        ipdb
        requests
        netaddr
        ipython
        # cython
        pycapnp
        path.py
        colored-traceback
        pudb
        colorlog
        msgpack-python
        pyblake2
        brotli
        pysodium
        ipfsapi
        curio
        """
        # self.pip(C, destpath)

        C = """
        set -ex
        cd %s
        rm -rf share
        rsync -rav lib/python3.6/site-packages/ lib/site-packages/
        rm -rf lib/python3.6
        find . -name '*.pyc' -delete
        find . -name '__pycache__' -delete
        find . -name 'get-pip.py' -delete
        set +ex  #TODO: *1 should not give error. but works
        find . -name "*.dist-info" -exec rm -rf {} \;
        find . -name "*.so" -exec mv {} . \;
        #copy all so to bin dir
        find lib -name "*.so" -exec mv {} bin/ \;

        """ % destpath
        self._cuisine.core.run(C)

    def pip(self, pips, destpath=""):
        if destpath == "":
            destpath = "$tmpDir/build/python/"
        destpath = self._cuisine.core.args_replace(destpath)
        for item in pips.split("\n"):
            item = item.strip()
            if item == "":
                continue
            # cannot use cuisine functionality because would not be sandboxed
            C = "set -ex;cd %s;source env.sh;pip3 install --trusted-host pypi.python.org %s" % (destpath, item)
            self._cuisine.core.run(C)

    def install(self):
        if self._cuisine.platformtype.osname == "debian":
            C = """
            libpython3.5-dev
            python3.5-dev
            """
        elif self._cuisine.platformtype.osname == 'ubuntu' and self._cuisine.platformtype.osversion == '16.04':
            C = """
            libpython3.5-dev
            python3.5-dev
            """
        else:
            C = """
            python3
            # postgresql
            # libpython3.4-dev
            # python3.4-dev
            libpython3.5-dev
            python3.5-dev
            """
        self._cuisine.package.multiInstall(C)

        C = """
        autoconf
        libffi-dev
        gcc
        make
        build-essential
        autoconf
        libtool
        pkg-config
        libpq-dev
        libsqlite3-dev
        """
        self._cuisine.package.multiInstall(C)
