from JumpScale import j
from ActionDecorator import ActionDecorator


class actionrun(ActionDecorator):

    def __init__(self, *args, **kwargs):
        ActionDecorator.__init__(self, *args, **kwargs)
        self.selfobjCode = "cuisine=j.tools.cuisine.getFromId('$id');selfobj=cuisine.capnp"


base = j.tools.cuisine.getBaseClass()


class CuisineCapnp(base):

    def __init__(self, executor, cuisine):
        self.executor = executor
        self.cuisine = cuisine

    @actionrun(action=True)
    def install(self):
        """
        install capnp
        """
        self.cuisine.package.mdupdate()
        self.cuisine.package.multiInstall(['curl', 'make', 'g++', 'python-dev'])

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
        self.cuisine.core.run_script(script)
        # install python pacakge
        self.cuisine.pip.multiInstall(['cython', 'setuptools', 'pycapnp'], upgrade=True)
