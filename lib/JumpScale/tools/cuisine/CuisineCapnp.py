from JumpScale import j
from ActionDecorator import ActionDecorator


class actionrun(ActionDecorator):

    def __init__(self, *args, **kwargs):
        ActionDecorator.__init__(self, *args, **kwargs)
        self.selfobjCode = "cuisine=j.tools.cuisine.getFromId('$id');selfobj=cuisine.capnp"


base = j.tools.cuisine.getBaseClass()


class CuisineCapnp(base):

    def __init__(self, executor, cuisine):
        self._executor = executor
        self._cuisine = cuisine

    
    def install(self):
        """
        install capnp
        """
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
