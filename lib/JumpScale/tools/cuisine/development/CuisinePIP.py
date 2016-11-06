
from JumpScale import j

base = j.tools.cuisine._getBaseClass()


class CuisinePIP(base):

    def __init__(self, executor, cuisine):
        self._executor = executor
        self._cuisine = cuisine

    # -----------------------------------------------------------------------------
    # PIP PYTHON PACKAGE MANAGER
    # -----------------------------------------------------------------------------

    def ensure(self):
        if self._cuisine.core.isMac:
            return

        self._cuisine.package.install('python3.5')
        self._cuisine.package.install('python3-pip')

        C = """
            #important remove olf pkg_resources, will conflict with new pip
            rm -rf /usr/lib/python3/dist-packages/pkg_resources
            cd $tmpDir/
            rm -rf get-pip.py
            wget --remote-encoding=utf-8 https://bootstrap.pypa.io/get-pip.py
            """
        C = self._cuisine.core.args_replace(C)
        self._cuisine.core.execute_bash(C)
        C = "python3 $tmpDir/get-pip.py"
        C = self._cuisine.core.args_replace(C)
        self._cuisine.core.run(C)

    def packageUpgrade(self, package):
        '''
        The "package" argument, defines the name of the package that will be upgraded.
        '''
        # self._cuisine.core.set_sudomode()
        self._cuisine.core.run('pip3 install --upgrade %s' % (package))

    def install(self, package=None, upgrade=False, doneCheckMethod=None):
        '''
        The "package" argument, defines the name of the package that will be installed.
        '''
        # self._cuisine.core.set_sudomode()
        if self._cuisine.core.isArch:
            if package in ["credis", "blosc", "psycopg2"]:
                return

        if self._cuisine.core.isCygwin and package in ["psycopg2", "psutil", "zmq"]:
            return

        if doneCheckMethod != None and doneCheckMethod(package) == True:
            print("No need to pip install:%s (already done)" % package)
            return

        cmd = "pip3 install %s" % package
        if upgrade:
            cmd += " --upgrade"
        self._cuisine.core.run(cmd)

    def packageRemove(self, package):
        '''
        The "package" argument, defines the name of the package that will be ensured.
        The argument "r" referes to the requirements file that will be used by pip and
        is equivalent to the "-r" parameter of pip.
        Either "package" or "r" needs to be provided
        '''
        return self._cuisine.core.run('pip3 uninstall %s' % (package))

    def multiInstall(self, packagelist, upgrade=False, doneCheckMethod=None):
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
            self.install(item, doneCheckMethod)
