from JumpScale import j
import sys
import os
import re


def _useELFtrick(file):
    fd = os.open(file, os.O_RDONLY)
    out = os.read(fd, 5)
    if out[0:4] != "\x7fELF":
        result = 0  # ELF trick fails...
    elif out[4] == '\x01':
        result = 32
    elif out[4] == '\x02':
        result = 64
    else:
        result = 0
    os.close(fd)
    return result


class PlatformTypes:

    def __init__(self):
        self.__jslocation__ = "j.core.platformtype"
        self._myplatform = None
        self._platformParents = {}
        self._platformParents["unix"] = ["generic"]
        self._platformParents["linux"] = ["unix"]
        self._platformParents["linux32"] = ["linux"]
        self._platformParents["linux64"] = ["linux"]
        self._platformParents["unix32"] = ["unix"]
        self._platformParents["unix64"] = ["unix"]
        self._platformParents["alpine"] = ["linux64"]
        self._platformParents["ubuntu"] = ["linux"]
        self._platformParents["ubuntu64"] = ["ubuntu", "linux64"]
        self._platformParents["ubuntu32"] = ["ubuntu", "linux32"]
        self._platformParents["mint64"] = ["mint", "ubuntu64"]
        self._platformParents["mint32"] = ["mint", "ubuntu32"]
        self._platformParents["win"] = ["generic"]
        self._platformParents["win32"] = ["win"]
        self._platformParents["win64"] = ["win"]
        self._platformParents["win7"] = ["win"]
        self._platformParents["win8"] = ["win"]
        self._platformParents["vista"] = ["win"]
        self._platformParents["cygwin32"] = ["cygwin"]
        self._platformParents["cygwin64"] = ["cygwin"]
        self._platformParents["win2008_64"] = ["win64"]
        self._platformParents["win2012_64"] = ["win64"]
        self._platformParents["cygwin_nt-10.064"] = ["win64", "cygwin64"]
        self._platformParents["cygwin_nt-10.032"] = ["win32", "cygwin32"]
        self._platformParents["arch"] = ["linux"]
        self._platformParents["arch32"] = ["arch", "linux32"]
        self._platformParents["arch64"] = ["arch", "linux64"]
        self._platformParents["darwin32"] = ["darwin", "unix32"]
        self._platformParents["darwin64"] = ["darwin", "unix64"]
        self._platformParents["debian"] = ["ubuntu"]
        self._platformParents["debian32"] = ["debian", "linux32"]
        self._platformParents["debian64"] = ["debian", "linux64"]

    @property
    def myplatform(self):
        if self._myplatform is None:
            self._myplatform = PlatformType()
        return self._myplatform

    def getParents(self, name):
        res = [name]
        res = self._getParents(name, res)
        return res

    def _getParents(self, name, res=[]):
        if name in self._platformParents:
            for item in self._platformParents[name]:
                if item not in res:
                    res.append(item)
                res = self._getParents(item, res)
        return res

    def get(self, executor=None):
        """
        @param executor is an executor object, None or $hostname:$port or $ipaddr:$port or $hostname or $ipaddr
        """
        return PlatformType(executor=executor)


# class Executor:
#
#     def __init__(self):
#         self.id = "localexec"
#
#     def execute(self, cmd, die=True, showout=True, **args):
#
#         childprocess = subprocess.Popen(cmd, stdin=subprocess.PIPE, stdout=subprocess.PIPE,
#                                         stderr=subprocess.PIPE, close_fds=True, shell=True, env=os.environ)
#         (output, error) = childprocess.communicate()
#         exitcode = childprocess.returncode
#
#         if showout:
#             print(output)
#             print(error)
#
#         return exitcode, output.decode(), error.decode()


class PlatformType:

    def __init__(self, name="", executor=None):
        self.myplatform = name
        # self._platformtypes={}
        # self._uname=""
        # self._is64bit=None
        # self._osversion=""
        # self._hostname=""
        # self._osname=""
        if executor is None:
            self.executor = j.tools.executor.getLocal()
            # self.executor = Executor()
        else:
            # if executor.addr == "localhost" or executor.addr == "127.0.0.1":
            #     self.executor = Executor()
            # else:
            self.executor = executor
        self.cache = j.data.cache.get(
            self.executor.id, "platformtype", keepInMem=True, reset=False)

        if name == "":
            self._getPlatform()

    @property
    def platformtypes(self):
        def get():
            platformtypes = j.core.platformtype.getParents(self.myplatform)
            platformtypes = [item for item in platformtypes if item != ""]
            return platformtypes
        return self.cache.get("platformtypes", get)

    @property
    def uname(self):
        def get():
            rc, self._uname, err = self.executor.execute("uname -mnprs", showout=False, timeout=3, die=False)
            self._uname = self._uname.strip()
            if self._uname.find("warning: setlocale") != -1:
                j.application._fixlocale = True
                os.environ["LC_ALL"] = 'C.UTF-8'
                os.environ["TERMINFO"] = 'xterm-256colors'
            _uname = self._uname.split("\n")[0]
            return _uname
        self._uname = self.cache.get("uname", get)
        self._osname0, self._hostname0, self._version, self._cpu, self._platform = self._uname.split(
            " ")
        return self._uname

    @property
    def hostname(self):
        self.uname
        return self._hostname0.split(".")[0]

    @property
    def is64bit(self):
        self.uname
        self._is64bit = "64" in self._cpu
        return self._is64bit

    @property
    def is32bit(self):
        self.uname
        self._is64bit = "32" in self._cpu
        return self._is64bit

    @property
    def osversion(self):
        self.osname  # will populate the version
        return self.cache.get("osversion")

    @property
    def osname(self):
        def get():
            self.uname
            self._osname = self._osname0.lower()
            self._osversion = "unknown"
            if self._osname not in ["darwin"] and not self._osname.startswith("cygwin"):

                rc, lsbcontent, err = self.executor.cuisine.core.run(
                    "cat /etc/lsb-release", replaceArgs=False, showout=False, die=False)
                if rc == 0:
                    import re
                    try:
                        self._osname = re.findall(
                            "DISTRIB_ID=(\w+)", lsbcontent)[0].lower()
                        self._osversion = re.findall(
                            "DISTRIB_RELEASE=([\w.]+)", lsbcontent)[0].lower()
                    except IndexError as e:
                        raise RuntimeError("Can't parse /etc/lsb-release")
                else:
                    pkgman2dist = {
                        'pacman': 'arch', 'apt-get': 'ubuntu', 'yum': 'fedora', 'apk': 'alpine'}
                    for pkgman, dist in pkgman2dist.items():
                        rc, _, err = self.executor.execute("which %s" % pkgman, showout=False, die=False)
                        if rc == 0:
                            self._osname = pkgman2dist[pkgman]
                            break
                    else:
                        raise j.exceptions.RuntimeError("Couldn't define os version.")
            self.cache.set("osversion", self._osversion)
            return self._osname

        return self.cache.get("osname", get)

    def checkMatch(self, match):
        """
        match is in form of linux64,darwin
        if any of the items e.g. darwin is in getMyRelevantPlatforms then return True
        """
        tocheck = self.platformtypes
        matches = [item.strip().lower()
                   for item in match.split(",") if item.strip() != ""]
        for match in matches:
            if match in tocheck:
                return True
        return False

    def _getPlatform(self):

        if self.is32bit:
            name = "%s32" % (self.osname)
        else:
            name = "%s64" % (self.osname)

        self.myplatform = name

    def has_parent(self, name):
        return name in self.platformtypes

    def dieIfNotPlatform(self, platform):
        if not self.has_parent(platform):
            raise j.exceptions.RuntimeError(
                "Can not continue, supported platform is %s, this platform is %s" % (platform, self.myplatform))

    def isUnix(self):
        '''Checks whether the platform is Unix-based'''
        return self.has_parent("unix")

    def isWindows(self):
        '''Checks whether the platform is Windows-based'''
        return self.has_parent("win")

    def isLinux(self):
        '''Checks whether the platform is Linux-based'''
        return self.has_parent("linux")

    def isGeneric(self):
        '''Checks whether the platform is generic (they all should)'''
        return self.has_parent("generic")

    def isXen(self):
        '''Checks whether Xen support is enabled'''
        return j.sal.process.checkProcessRunning('xen') == 0

    def isVirtualBox(self):
        '''Check whether the system supports VirtualBox'''
        if self.isWindows():
            # TODO: P3 Implement proper check if VBox on Windows is supported
            return False
        exitcode, stdout, stderr = j.sal.process.run(
            'lsmod |grep vboxdrv |grep -v grep', stopOnError=False)
        return exitcode == 0

    def isHyperV(self):
        '''Check whether the system supports HyperV'''
        # TODO: should be moved to _getPlatform & proper parent definition
        if self.isWindows():
            import winreg as wr
            try:
                virt = wr.OpenKey(
                    wr.HKEY_LOCAL_MACHINE, 'SOFTWARE\Microsoft\Windows NT\CurrentVersion\Virtualization', 0, wr.KEY_READ | wr.KEY_WOW64_64KEY)
                wr.QueryValueEx(virt, 'Version')
            except WindowsError:
                return False
            return True
        return False

    def __str__(self):
        return str(self.myplatform)

    __repr__ = __str__
