
from JumpScale import j

base = j.tools.cuisine._getBaseClass()


class CuisinePackage(base):

    def __init__(self, executor, cuisine):
        self.logger = j.logger.get('j.tools.cuisine.package')
        self._executor = executor
        self._cuisine = cuisine

    def _repository_ensure_apt(self, repository):
        self.ensure('python-software-properties')
        self._cuisine.core.sudo("add-apt-repository --yes " + repository)

    def _apt_get(self, cmd):
        CMD_APT_GET = 'DEBIAN_FRONTEND=noninteractive apt-get -q --yes -o Dpkg::Options::="--force-confdef" -o Dpkg::Options::="--force-confold" '
        cmd = CMD_APT_GET + cmd
        result = self._cuisine.core.sudo(cmd)
        # If the installation process was interrupted, we might get the following message
        # E: dpkg was interrupted, you must manually self._cuisine.core.run 'sudo
        # dpkg --configure -a' to correct the problem.
        if "sudo dpkg --configure -a" in result:
            self._cuisine.core.sudo("DEBIAN_FRONTEND=noninteractive dpkg --configure -a")
            result = self._cuisine.core.sudo(cmd)
        return result

    def update(self, package=None):
        if self._cuisine.core.isUbuntu:
            if package is None:
                return self._apt_get("-q --yes update")
            else:
                if type(package) in (list, tuple):
                    package = " ".join(package)
                return self._apt_get(' upgrade ' + package)
        else:
            raise j.exceptions.RuntimeError("could not install:%s, platform not supported" % package)

    def mdupdate(self):
        """
        update metadata of system
        """
        self.logger.info("packages mdupdate")
        if self._cuisine.core.isUbuntu:
            self._cuisine.core.run("apt-get update")
        elif self._cuisine.core.isMac:
            location = self._cuisine.core.command_location("brew")
            # self._cuisine.core.run("sudo chown root %s" % location)
            self._cuisine.core.run("brew update")
        elif self._cuisine.core.isArch:
            self._cuisine.core.run("pacman -Syy")

    def upgrade(self, distupgrade=False):
        """
        upgrades system, distupgrade means ubuntu 14.04 will fo to e.g. 15.04
        """
        self.mdupdate()
        self.logger.info("packages upgrade")
        if self._cuisine.core.isUbuntu:
            if distupgrade:
                return self._apt_get("dist-upgrade")
            else:
                return self._apt_get("upgrade")
        elif self._cuisine.core.isArch:
            self._cuisine.core.run("pacman -Syu --noconfirm;pacman -Sc --noconfirm")
        elif self._cuisine.core.isMac:
            self._cuisine.core.run("brew upgrade")
        elif self._cuisine.core.isCygwin:
            return  # no such functionality in apt-cyg
        else:
            raise j.exceptions.RuntimeError("could not upgrade, platform not supported")

    def install(self, package, allow_unauthenticated=False):

        if self._cuisine.core.isUbuntu:
            cmd = "apt-get install -y "
            if allow_unauthenticated:
                cmd += ' --allow-unauthenticated '
            cmd += package

        elif self._cuisine.core.isArch:
            if package.startswith("python3"):
                package = "extra/python"

            # ignore
            if package in ["libpython3.5-dev", "libffi-dev", "build-essential", "libpq-dev", "libsqlite3-dev"]:
                return

            cmd = "pacman -S %s  --noconfirm" % package

        elif self._cuisine.core.isMac:
            if package in ["libpython3.4-dev", "python3.4-dev", "libpython3.5-dev", "python3.5-dev", "libffi-dev", "make", "build-essential", "libpq-dev", "libsqlite3-dev"]:
                return

            _, installed, _ = self._cuisine.core.run("brew list")
            if package in installed:
                return  # means was installed

            # rc,out=self._cuisine.core.run("brew info --json=v1 %s"%package,showout=False,die=False)
            # if rc==0:
            #     info=j.data.serializer.json.loads(out)
            #     return #means was installed

            if "wget" == package:
                package = "%s --enable-iri" % package

            cmd = "brew install %s " % package

        elif self._cuisine.core.isCygwin:
            if package in ["sudo", "net-tools"]:
                return

            installed = self._cuisine.core.run("apt-cyg list&")[1].splitlines()
            if package in installed:
                return  # means was installed

            cmd = "apt-cyg install %s&" % package
        else:
            raise j.exceptions.RuntimeError("could not install:%s, platform not supported" % package)

        mdupdate = False
        while True:
            rc, out, err = self._cuisine.core.run(cmd, die=False)

            if rc > 0:
                if mdupdate is True:
                    raise j.exceptions.RuntimeError("Could not install:'%s' \n%s" % (package, out))

                if out.find("not found") != -1 or out.find("failed to retrieve some files") != -1:
                    self.mdupdate()
                    mdupdate = True
                    continue

                raise j.exceptions.RuntimeError("Could not install:%s %s" % (package, err))

            return out

    def multiInstall(self, packagelist, allow_unauthenticated=False):
        """
        @param packagelist is text file and each line is name of package
        can also be list

        e.g.
            # python
            mongodb

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
                dep = dep.strip()
                if dep is None or dep == "":
                    continue
                self.install(dep, allow_unauthenticated=allow_unauthenticated)
        finally:
            self._cuisine.core.sudomode = previous_sudo

    def start(self, package):
        if self._cuisine.core.isArch or self._cuisine.core.isUbuntu or self._cuisine.core.isMac:
            self._cuisine.processmanager.ensure(package)
        else:
            raise j.exceptions.RuntimeError("could not install/ensure:%s, platform not supported" % package)

    def ensure(self, package, update=False):
        """Ensure apt packages are installed"""
        if self._cuisine.core.isUbuntu:
            if isinstance(package, str):
                package = package.split()
            res = {}
            for p in package:
                p = p.strip()
                if not p:
                    continue
                # The most reliable way to detect success is to use the command status
                # and suffix it with OK. This won't break with other locales.
                _, status, _ = self._cuisine.core.run("dpkg-query -W -f='${Status} ' %s && echo **OK**;true" % p)
                if not status.endswith("OK") or "not-installed" in status:
                    self.install(p)
                    res[p] = False
                else:
                    if update:
                        self.update(p)
                    res[p] = True
            if len(res) == 1:
                for _, value in res.items():
                    return value
            else:
                return res
        elif self._cuisine.core.isArch:
            self._cuisine.core.run("pacman -S %s" % package)
        else:
            raise j.exceptions.RuntimeError("could not install/ensure:%s, platform not supported" % package)

        raise j.exceptions.RuntimeError("not supported platform")

    def clean(self, package=None, agressive=False):
        """
        clean packaging system e.g. remove outdated packages & caching packages
        @param agressive if True will delete full cache

        """
        if self._cuisine.core.isUbuntu:
            if package != None:
                return self._apt_get("-y --purge remove %s" % package)
            else:
                self._cuisine.core.run("apt-get autoremove -y")

            self._apt_get("autoclean")
            C = """
            apt-get clean
            rm -rf /bd_build
            rm -rf /tmp/* /var/tmp/*
            rm -f /etc/dpkg/dpkg.cfg.d/02apt-speedup

            find -regex '.*__pycache__.*' -delete
            rm -rf /var/log
            mkdir -p /var/log/apt
            rm -rf /var/tmp
            mkdir -p /var/tmp

            """
            self._cuisine.core.execute_bash(C)

        elif self._cuisine.core.isArch:
            cmd = "pacman -Sc"
            if agressive:
                cmd += "c"
            self._cuisine.core.run(cmd)
            if agressive:
                self._cuisine.core.run("pacman -Qdttq", showout=False)

        elif self._cuisine.core.isMac:
            if package:
                self._cuisine.core.run("brew cleanup %s" % package)
                self._cuisine.core.run("brew remove %s" % package)
            else:
                self._cuisine.core.run("brew cleanup")

        elif self._cuisine.core.isCygwin:
            if package:
                self._cuisine.core.run("apt-cyg remove %s" % package)
            else:
                pass

        else:
            raise j.exceptions.RuntimeError("could not package clean:%s, platform not supported" % package)

    def remove(self, package, autoclean=False):
        if self._cuisine.core.isUbuntu:
            self._apt_get('remove ' + package)
            if autoclean:
                self._apt_get("autoclean")
        elif self.isMac:
            self._cuisine.core.run("brew remove %s" % package)

    def __repr__(self):
        return "cuisine.package:%s:%s" % (self._executor.addr, self._executor.port)

    __str__ = __repr__
