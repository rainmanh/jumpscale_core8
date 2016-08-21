
from JumpScale import j

base = j.tools.cuisine._getBaseClass()


class CuisineBase(base):
    """
    the base for any install
    """

    def install(self):
        self._cuisine.bash.fixlocale()

        if self._cuisine.core.isMac:
            C = ""
        else:
            C = """
            sudo
            net-tools
            python3
            """

        C += """
        openssl
        wget
        curl
        git
        mc
        tmux
        """
        out = ""
        # make sure all dirs exist
        for key, item in self._cuisine.core.dir_paths.items():
            out += "mkdir -p %s\n" % item
        self._cuisine.core.run_script(out)

        self._cuisine.package.mdupdate()

        if not self._cuisine.core.isMac and not self._cuisine.core.isCygwin:
            self._cuisine.package.install("fuse")

        if self._cuisine.core.isArch:
            self._cuisine.package.install("wpa_actiond")  # is for wireless auto start capability
            self._cuisine.package.install("redis-server")

        self._cuisine.package.multiInstall(C)
        self._cuisine.package.upgrade()

        self._cuisine.package.clean()

        self._cuisine.bash.addPath(j.sal.fs.joinPaths(self._cuisine.core.dir_paths["base"], "bin"))
