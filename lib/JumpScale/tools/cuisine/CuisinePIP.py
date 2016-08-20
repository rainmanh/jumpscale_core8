
from JumpScale import j

from ActionDecorator import ActionDecorator


class actionrun(ActionDecorator):

    def __init__(self, *args, **kwargs):
        ActionDecorator.__init__(self, *args, **kwargs)
        self.selfobjCode = "cuisine=j.tools.cuisine.getFromId('$id');selfobj=cuisine.pip"

base = j.tools.cuisine.getBaseClass()


class CuisinePIP(base):

    def __init__(self, executor, cuisine):
        self._executor = executor
        self._cuisine = cuisine

    # -----------------------------------------------------------------------------
    # PIP PYTHON PACKAGE MANAGER
    # -----------------------------------------------------------------------------

    
    def upgrade(self, package):
        '''
        The "package" argument, defines the name of the package that will be upgraded.
        '''
        self._cuisine.core.set_sudomode()
        self._cuisine.core.run('pip3 install --upgrade %s' % (package))

    
    def install(self, package=None, upgrade=False):
        '''
        The "package" argument, defines the name of the package that will be installed.
        '''
        self._cuisine.core.set_sudomode()
        if self._cuisine.core.isArch:
            if package in ["credis", "blosc", "psycopg2"]:
                return

        if self._cuisine.core.isCygwin and package in ["psycopg2", "psutil", "zmq"]:
            return

        cmd = "pip3 install %s" % package
        if upgrade:
            cmd += " --upgrade"
        self._cuisine.core.run(cmd)

    
    def remove(self, package):
        '''
        The "package" argument, defines the name of the package that will be ensured.
        The argument "r" referes to the requirements file that will be used by pip and
        is equivalent to the "-r" parameter of pip.
        Either "package" or "r" needs to be provided
        '''
        return self._cuisine.core.run('pip3 uninstall %s' % (package))

    
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

        @param runid, if specified actions will be used to execute
        """
        previous_sudo = self._cuisine.core.sudomode
        try:
            self._cuisine.core.sudomode = True

            if j.data.types.string.check(packagelist):
                packages = packagelist.split("\n")
            elif j.data.types.list.check(packagelist):
                packages = packagelist
            else:
                raise j.exceptions.Input('packagelist should be string or a list. received a %s' % type(packagelist))

                for dep in packages:
                    dep = dep.strip()
                    if dep.strip() == "":
                        continue
                    if dep.strip()[0] == "#":
                        continue
                    self.install(dep)
        finally:
            self._cuisine.core.sudomode = previous_sudo
