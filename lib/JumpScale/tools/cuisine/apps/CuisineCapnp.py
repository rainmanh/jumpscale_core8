from JumpScale import j

base = j.tools.cuisine._getBaseClass()


class CuisineCapnp(base):

    def __init__(self, executor, cuisine):
        self._executor = executor
        self._cuisine = cuisine

    def install(self, reset=False):
        """
        install capnp
        """

        if reset == False and self.isInstalled():
            return

        self._cuisine.package.mdupdate()
        self._cuisine.package.multiInstall(['curl', 'make', 'g++', 'python-dev'])

        # c++ deps libs
        script = """
        cd $tmpDir
        curl -O https://capnproto.org/capnproto-c++-0.5.3.tar.gz
        tar zxf capnproto-c++-0.5.3.tar.gz
        cd capnproto-c++-0.5.3
        ./configure
        make -j6 check
        sudo make install
        """
        self._cuisine.core.run_script(script)
        # install python pacakge
        self._cuisine.pip.multiInstall(['cython', 'setuptools', 'pycapnp'], upgrade=True)
