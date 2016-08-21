
from JumpScale import j

base = j.tools.cuisine._getBaseClass()


class CuisineJS8_G8OS(base):

    def jumpscale_installed(self, die=False):
        rc1, out1, err = self._cuisine.core.run('which js8', die=False)
        rc2, out2, err = self._cuisine.core.run('which js', die=False)
        if (rc1 == 0 and out1) or (rc2 == 0 and out2):
            return True
        return False

    def jumpscale8(self, rw=False, reset=False):
        """
        install jumpscale, will be done as sandbox

        @param rw if True install sandbox in RW mode
        @param reset, remove old code (only used when rw mode)

        """
        import time
        if self.jumpscale_installed() and not reset:
            return
        self.clean()
        self.base()

        C = """
            js8 stop
            set -ex
            cd /usr/bin
            rm -f js8
            cd /usr/local/bin
            rm -f js8
            rm -f /usr/local/bin/jspython
            rm -f /usr/local/bin/js
            rm -fr /opt/*
            """
        self._cuisine.core.run_script(C)

        if not self._cuisine.core.isUbuntu:
            raise j.exceptions.RuntimeError("not supported yet")

        if reset:
            C = """
                set +ex
                rm -rf /opt
                rm -rf /optrw
                """
            self._cuisine.core.run_script(C)

        C = """
            wget https://stor.jumpscale.org/storx/static/js8 -O /usr/local/bin/js8
            chmod +x /usr/local/bin/js8
            cd /
            mkdir -p $base
            """
        self._cuisine.core.run_script(C)

        """
        install jumpscale8 sandbox in read or readwrite mode
        """
        C = """
            set -ex
            rm -rf /opt
            cd /usr/local/bin
            """
        if rw:
            C += "./js8 -rw init"
        else:
            C += "./js8 init"
        self._cuisine.core.run_script(C)

        start = j.data.time.epoch
        timeout = 30
        while start + timeout > j.data.time.epoch:
            if not self._cuisine.core.file_exists('/opt/jumpscale8/bin/jspython'):
                time.sleep(2)
            else:
                self._cuisine.core.file_link('/opt/jumpscale8/bin/jspython', '/usr/local/bin/jspython')
                self._cuisine.core.file_link('/opt/jumpscale8/bin/js', '/usr/local/bin/js')
                self._cuisine.bash.include('/opt/jumpscale8/env.sh')
                break

        print("* re-login into your shell to have access to js, because otherwise the env arguments are not set properly.")

    def base(self):
        self.clean()

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
