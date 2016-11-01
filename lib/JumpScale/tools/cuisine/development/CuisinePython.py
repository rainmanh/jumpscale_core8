from JumpScale import j

base = j.tools.cuisine._getBaseClass()


class CuisinePython(base):

    def __init__(self, executor, cuisine):
        self._executor = executor
        self._cuisine = cuisine

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
