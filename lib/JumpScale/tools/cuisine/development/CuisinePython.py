from JumpScale import j

base = j.tools.cuisine._getBaseClass()


class CuisinePython(base):

    def _init(self):
        self.BUILDDIR = self.replace("$BUILDDIR/python3/")
        self.CODEDIR = self.replace("$CODEDIR/mercurial/cpython/")

    def build(self,  reset=False):
        """
        """
        if self.doneGet("build") and not reset:
            return

        self.cuisine.development.openssl.build(reset=reset)

        if reset:
            self.cuisine.core.run("rm -rf %s" % self.BUILDDIR)

        if self.cuisine.core.isMac:
            if not self.doneGet("xcode_install"):
                self.cuisine.core.run("xcode-select --install", die=False, showout=True)
                C = """
                openssl
                xz
                """
                self.cuisine.package.multiInstall(C)
                self.doneSet("xcode_install")

        if not self.doneGet("compile") or reset:
            self.cuisine.development.mercurial.pullRepo("https://hg.python.org/cpython", reset=reset)
            self.cuisine.core.run("set -ex;cd %s;hg update 3.6" % self.CODEDIR)

            if self.cuisine.core.isMac:
                openssldir = self.cuisine.development.openssl.BUILDDIR
                openSSlIncludeLine = ":%s:%s/include" % (openssldir, openssldir)
                C = 'cd %s;CPPFLAGS="-I%s/include";LDFLAGS="-L%s";./configure' % (self.CODEDIR, openssldir, openssldir)
            else:
                C = "cd %s;./configure" % self.CODEDIR

            self.log("configure python3")
            self.log(C)
            self.cuisine.core.file_write("%s/myconfigure.sh" % self.CODEDIR, C, replaceArgs=True)

            C = "cd %s;sh myconfigure.sh" % self.CODEDIR
            self.cuisine.core.run(C)

            C = "cd %s;make -s -j4" % self.CODEDIR
            self.log("compile python3")
            self.log(C)
            self.cuisine.core.run(C)
        self.doneSet("compile")

        # find buildpath for lib (depending source it can be other destination)
        # is the core python binaries
        libBuildName = [item for item in self.cuisine.core.run(
            "ls %s/build" % self.CODEDIR)[1].split("\n") if item.startswith("lib")][0]
        lpath = j.sal.fs.joinPaths(self.CODEDIR, "build", libBuildName)
        self.cuisine.core.copyTree(source=lpath, dest=self.BUILDDIR, keepsymlinks=False, deletefirst=False,
                                   overwriteFiles=True, recursive=True, rsyncdelete=False, createdir=True)

        # copy python libs (non compiled)
        ignoredir = ["test", "tkinter", "turtledemo",
                     "msilib", "pydoc*", "lib2to3", "idlelib"]
        lpath = self.replace("$CODEDIR/lib")
        ldest = self.replace("$BUILDDIR/plib")
        self.cuisine.core.copyTree(source=lpath, dest=ldest, keepsymlinks=False, deletefirst=False,
                                   overwriteFiles=True, ignoredir=ignoredir,
                                   recursive=True, rsyncdelete=True, createdir=True)

        self.cuisine.core.file_copy("%s/python.exe" % self.CODEDIR, "%s/python3" % self.BUILDDIR)

        # copy includes
        lpath = j.sal.fs.joinPaths(self.CODEDIR, "Include",)
        ldest = j.sal.fs.joinPaths(self.BUILDDIR, "include/python")
        self.cuisine.core.copyTree(source=lpath, dest=ldest, keepsymlinks=False, deletefirst=False,
                                   overwriteFiles=True, ignoredir=ignoredir,
                                   recursive=True, rsyncdelete=False, createdir=True)

        # now copy openssl parts in
        self.cuisine.core.copyTree(source=self.cuisine.development.openssl.BUILDDIR, dest=self.BUILDDIR,
                                   keepsymlinks=False, deletefirst=False,
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

        self.cuisine.core.file_write("%s/env.sh" % self.BUILDDIR, C, replaceArgs=True)

        if not self.doneGet("pip3install") or reset:
            C = """
            set -ex
            cd $BUILDDIR
            source env.sh
            rm -rf get-pip.py
            curl https://bootstrap.pypa.io/get-pip.py > get-pip.py
            python3 get-pip.py
            """
            self.cuisine.core.run(self.replace(C))
        self.doneSet("pip3install")

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
        self.pip(C, reset=reset)

        msg = "to test do:\ncd $BUILDDIR;source env.sh;python3"
        msg = self.replace(msg)
        self.log(msg)
        self.doneSet("build")

    def sandbox(self, reset=False):
        self.build(reset=reset)
        if self.doneGet("sandbox") and not reset:
            return

        from IPython import embed
        print("DEBUG NOW sandbox")
        embed()
        raise RuntimeError("stop debug here")

        C = """
        set -ex
        cd $BUILDDIR
        rm -rf share
        rsync -rav lib/python3.6/site-packages/ plib/site-packages/
        rm -rf lib/python3.6
        find . -name '*.pyc' -delete

        find . -name 'get-pip.py' -delete
        set +ex  #TODO: *1 should not give error. but works
        find -L .  -name '__pycache__' -exec rm -rf {} \;
        find . -name "*.dist-info" -exec rm -rf {} \;
        find . -name "*.so" -exec mv {} lib/ \;

        """
        self.cuisine.core.run(self.replace(C))

        # now copy jumpscale in
        linkpath = "%s/lib/JumpScale" % self.cuisine.core.dir_paths["base"]
        C = "ln -s %s %s/lib/JumpScale" % (linkpath, self.BUILDDIR)
        if not self.cuisine.core.file_exists("%s/lib/JumpScale" % self.BUILDDIR):
            self.cuisine.core.run(C)

        # now create packaged dir
        destpath2 = self.BUILDDIR.rstrip("/").rstrip() + "2"
        self.cuisine.core.copyTree(source=self.BUILDDIR, dest=destpath2, keepsymlinks=False, deletefirst=True,
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
        # self.cuisine.core.run(C)

        self.doneSet("sandbox")

    def pip(self, pips, reset=False):
        for item in pips.split("\n"):
            item = item.strip()
            if item == "":
                continue
            # cannot use cuisine functionality because would not be sandboxed
            if self.doneGet("pip3_%s" % item) or reset:
                C = "set -ex;cd $BUILDDIR;source env.sh;pip3 install --trusted-host pypi.python.org %s" % item
                self.cuisine.core.run(self.replace(C))
                self.doneSet("pip3_%s" % item)

    def install(self):
        if self.cuisine.platformtype.osname == "debian":
            C = """
            libpython3.5-dev
            python3.5-dev
            """
        elif self.cuisine.platformtype.osname == 'ubuntu' and self.cuisine.platformtype.osversion == '16.04':
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
        self.cuisine.package.multiInstall(C)

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
        self.cuisine.package.multiInstall(C)
