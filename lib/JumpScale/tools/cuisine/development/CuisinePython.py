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

        ldir = "$TMPDIR/build/openssl"
        ldir = self._cuisine.core.args_replace(ldir)

        if not self._cuisine.core.dir_exists(ldir) or reset:
            self._cuisine.development.openssl.build(reset=reset)

        return ldir

    def build(self, destpath="", reset=False):
        """
        @param destpath, if '' then will be $TMPDIR/build/python
        """

        self.checkOpenSSL(reset=reset)

        if destpath == "":
            destpath = "$TMPDIR/build/python/"
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
                                    recursive=True, rsyncdelete=False, createdir=True)

        ignoredir = ["test", "tkinter", "turtledemo",
                     "msilib", "pydoc*", "lib2to3", "idlelib"]
        lpath = j.sal.fs.joinPaths(cpath, "lib",)
        ldest = "%s/plib" % destpath
        self._cuisine.core.copyTree(source=lpath, dest=ldest, keepsymlinks=False, deletefirst=False,
                                    overwriteFiles=True, ignoredir=ignoredir,
                                    recursive=True, rsyncdelete=True, createdir=True)

        self._cuisine.core.file_copy("%s/python.exe" % cpath, "%s/python3" % destpath)

        # copy includes
        lpath = j.sal.fs.joinPaths(cpath, "Include",)
        ldest = j.sal.fs.joinPaths(destpath, "include/python")
        self._cuisine.core.copyTree(source=lpath, dest=ldest, keepsymlinks=False, deletefirst=False,
                                    overwriteFiles=True, ignoredir=ignoredir,
                                    recursive=True, rsyncdelete=False, createdir=True)

        # now copy openssl parts in
        sslpath = self.checkOpenSSL()
        self._cuisine.core.copyTree(source=sslpath, dest=destpath, keepsymlinks=False, deletefirst=False,
                                    overwriteFiles=True, ignoredir=ignoredir,
                                    recursive=True, rsyncdelete=False, createdir=True)

        C = """

        export JSBASE=`pwd`

        export PATH=$JSBASE:$JSBASE/bin:$JSBASE/lib/$JSPATH:/usr/local/bin:/usr/bin:/bin

        #export LUA_PATH="/opt/jumpscale8/lib/lua/?.lua;./?.lua;/opt/jumpscale8/lib/lua/?/?.lua;/opt/jumpscale8/lib/lua/tarantool/?.lua;/opt/jumpscale8/lib/lua/?/init.lua"

        export PYTHONPATH=$JSBASE/plib:$JSBASE/plib.zip:$JSBASE:$JSBASE/lib:$JSBASE/plib/site-packages:$JSBASE/lib/python3.6/site-packages
        export PYTHONHOME=$JSBASE
        export CPATH=$JSBASE/include:$JSBASE/include/openssl:$JSBASE/lib:$JSBASE/include/python

        export LC_ALL=en_US.UTF-8
        export LANG=en_US.UTF-8

        export LD_LIBRARY_PATH=$JSBASE/bin:$JSBASE/lib
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
        uvloop
        """
        self.pip(C, destpath)

        msg = "to test do:\ncd %s;source env.sh;python3" % destpath
        msg = self._cuisine.core.args_replace(msg)
        print(msg)
        return destpath

    def sandbox(self, build=False, reset=False, destpath=""):
        if destpath == "":
            destpath = "$TMPDIR/build/python/"
        destpath = self._cuisine.core.args_replace(destpath)

        if build or not self._cuisine.core.dir_exists(destpath):
            self.build(destpath, reset)

        C = """
        set -ex
        cd %s
        rm -rf share
        rsync -rav lib/python3.6/site-packages/ plib/site-packages/
        rm -rf lib/python3.6
        find . -name '*.pyc' -delete

        find . -name 'get-pip.py' -delete
        set +ex  #TODO: *1 should not give error. but works
        find -L .  -name '__pycache__' -exec rm -rf {} \;
        find . -name "*.dist-info" -exec rm -rf {} \;
        find . -name "*.so" -exec mv {} lib/ \;

        """ % destpath
        self._cuisine.core.run(C)

        # now copy jumpscale in
        linkpath = "%s/lib/JumpScale" % self._cuisine.core.dir_paths["base"]
        C = "ln -s %s %s/lib/JumpScale" % (linkpath, destpath)
        if not self._cuisine.core.file_exists("%s/lib/JumpScale" % destpath):
            self._cuisine.core.run(C)

        # now create packaged dir
        destpath2 = destpath.rstrip("/").rstrip() + "2"
        self._cuisine.core.copyTree(source=destpath, dest=destpath2, keepsymlinks=False, deletefirst=True,
                                    overwriteFiles=True,
                                    recursive=True, rsyncdelete=True, createdir=True)

        # zip trick does not work yet lets leave for now
        # C = """
        # set -ex
        # cd %s/plib
        # zip -r ../plib.zip *
        # cd ..
        # rm -rf plib
        # """ % destpath2
        # self._cuisine.core.run(C)

        # make sure we have ipfs available
        self._cuisine.apps.ipfs.start()

    def pip(self, pips, destpath=""):
        if destpath == "":
            destpath = "$TMPDIR/build/python/"
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
