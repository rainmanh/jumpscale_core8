
from JumpScale import j

base = j.tools.cuisine._getBaseClass()


class CuisinePIP(base):

    # -----------------------------------------------------------------------------
    # PIP PYTHON PACKAGE MANAGER
    # -----------------------------------------------------------------------------

    def ensure(self):
        if self.cuisine.core.isMac:
            return

        # python should already be requirement, do not install !! (despiegk)
        # self.cuisine.package.install('python3.5')
        # self.cuisine.package.install('python3-pip')

        C = """
            #important remove olf pkg_resources, will conflict with new pip
            rm -rf /usr/lib/python3/dist-packages/pkg_resources
            cd $TMPDIR/
            rm -rf get-pip.py
            #wget --remote-encoding=utf-8 https://bootstrap.pypa.io/get-pip.py
            curl https://bootstrap.pypa.io/get-pip.py >  get-pip.py
            """
        C = self.replace(C)
        self.cuisine.core.execute_bash(C)
        C = "python3 $TMPDIR/get-pip.py"
        C = self.replace(C)
        self.cuisine.core.run(C)

    def packageUpgrade(self, package):
        '''
        The "package" argument, defines the name of the package that will be upgraded.
        '''
        # self.cuisine.core.set_sudomode()
        self.cuisine.core.run('pip3 install --upgrade %s' % (package))

    def install(self, package=None, upgrade=False):
        '''
        The "package" argument, defines the name of the package that will be installed.
        '''
        # self.cuisine.core.set_sudomode()
        if self.cuisine.core.isArch:
            if package in ["credis", "blosc", "psycopg2"]:
                return

        if self.cuisine.core.isCygwin and package in ["psycopg2", "psutil", "zmq"]:
            return

        if not self.doneGet("pip_%s" % package):
            cmd = "pip3 install %s" % package
            if upgrade:
                cmd += " --upgrade"
            self.cuisine.core.run(cmd)
            self.doneSet("pip_%s" % package)

    def packageRemove(self, package):
        '''
        The "package" argument, defines the name of the package that will be ensured.
        The argument "r" referes to the requirements file that will be used by pip and
        is equivalent to the "-r" parameter of pip.
        Either "package" or "r" needs to be provided
        '''
        if not self.doneGet("pip_remove_%s" % package):
            return self.cuisine.core.run('pip3 uninstall %s' % (package))
            self.doneSet("pip_remove_%s" % package)

    def multiInstall(self, packagelist, upgrade=False):
        """
        @param packagelist is text file and each line is name of package
        can also be list

        e.g.
            # influxdb
            # ipdb
            # ipython
            # ipython-genutils
            itsdangerous
            Jinja2
            # marisa-trie
            MarkupSafe
            mimeparse
            mongoengine

        if doneCheckMethod!=None:
            it will ask for each pip if done or not to that method, if it returns true then already done

        """
        if j.data.types.string.check(packagelist):
            packages = packagelist.split("\n")
        elif j.data.types.list.check(packagelist):
            packages = packagelist
        else:
            raise j.exceptions.Input('packagelist should be string or a list. received a %s' % type(packagelist))

        to_install = []
        for dep in packages:
            dep = dep.strip()
            if dep is None or dep == "" or dep[0] == '#':
                continue
            to_install.append(dep)

        for item in to_install:
            self.install(item)
