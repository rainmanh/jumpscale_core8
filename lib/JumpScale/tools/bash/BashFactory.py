from JumpScale import j
import re
from io import StringIO


class Profile:
    env_pattern = re.compile(r'^([^=\n]+)="([^"\n]+)"$', re.MULTILINE)
    include_pattern = re.compile(r'^source (.*)$', re.MULTILINE)

    def __init__(self, bash, profilePath=""):
        """
        X="value"
        Y="value"
        PATH="p1:p2:p3"

        export X
        export Y
        """
        self.bash = bash
        self.home = bash.home
        self.cuisine = bash.cuisine
        self._env = {}
        self._path = set()
        self._includes = set()

        if profilePath == "":
            self.pathProfile = j.sal.fs.joinPaths(self.home, ".profile_js")
        else:
            self.pathProfile = profilePath

        content = self.cuisine.core.file_read(profilePath)

        for match in Profile.env_pattern.finditer(content):
            self._env[match.group(1)] = match.group(2)
        for match in Profile.include_pattern.finditer(content):
            self._includes.add(match.group(1))

        # load path
        if 'PATH' in self._env:
            path = self._env['PATH']
            _path = set(path.split(':'))
        else:
            _path = set()

        for item in _path:
            if item.strip() == "":
                continue
            if item.find("PATH") != -1:
                continue
            self.addPath(item)

        self._env.pop('PATH', None)

    def addPath(self, path):
        path = path.strip()
        path = path.replace("//", "/")
        path = path.replace("//", "/")
        path = path.rstrip("/")
        if path not in self._path:
            self._path.add(path)

    def addInclude(self, path):
        path = path.strip()
        path = path.replace("//", "/")
        path = path.replace("//", "/")
        path = path.rstrip("/")
        if path not in self._includes:
            self._includes.add(path)

    @property
    def paths(self):
        return list(self._path)

    def envSet(self, key, value):
        self._env[key] = value

    def envGet(self, key):
        return self._env[key]

    def envExists(self, key):
        return key in self._env

    def envDelete(self, key):
        del self._env[key]

    def __str__(self):
        self._env['PATH'] = ':'.join(set(self.paths)) + ":$PATH"

        content = StringIO()
        content.write('# environment variables\n')
        for key, value in self._env.items():
            content.write('%s="%s"\n' % (key, value))
            content.write('export %s\n\n' % key)

        content.write('# includes\n')
        for path in self._includes:
            content.write('source %s\n' % path)

        self._env.pop('PATH')

        return content.getvalue()

    __repr__ = __str__

    @property
    def env(self):
        return self._env

    def replace(self, text):
        """
        will look for $ENVNAME 's and replace them in text
        """
        for key, val in self.env.items():
            text = text.replace("$%s" % key, val)
        return text

    def save(self, includeInDefaultProfile=True):
        """
        save to disk
        @param includeInDefaultProfile, if True then will include in the default profile
        """

        # make sure we include our custom profile in the default
        if includeInDefaultProfile is True:
            out = ""
            for line in self.cuisine.core.file_read(self.bash.profileDefault.pathProfile).split("\n"):
                if line.find(self.pathProfile) != -1:
                    continue
                out += "%s\n" % line
            out += "\nsource %s\n" % self.pathProfile
            self.cuisine.core.file_write(self.bash.profileDefault.pathProfile, out)

        self.cuisine.core.file_write(self.pathProfile, str(self), showout=False)

        self.bash.reset()#do not remove !

    def getLocaleItems(self, force=False, showout=False):
        out = self.cuisine.core.run("locale -a")[1]
        return out.split("\n")

    def fixlocale(self):
        items = self.getLocaleItems()
        if "en_US.UTF-8" in items or "en_US.utf8" in items:
            self.envSet("LC_ALL", "en_US.UTF-8")
            self.envSet("LANG", "en_US.UTF-8")
            return
        elif "C.UTF-8" in items or "c.utf8" in items:
            self.envSet("LC_ALL", "C.UTF-8")
            self.envSet("LANG", "C.UTF-8")
            return

        raise j.exceptions.Input("Cannot find C.UTF-8, cannot fix locale's")


class BashFactory:

    def __init__(self):
        self.__jslocation__ = "j.tools.bash"

    def get(self, executor=None):
        """
        if executor==None then will be local
        """
        b = Bash(executor=executor)
        return b


class Bash:

    def __init__(self, executor=None):
        if executor is not None:
            self.executor = executor
        else:
            self.executor = j.tools.executor.getLocal()

        self.cuisine = self.executor.cuisine
        self.reset()

    def reset(self):
        self._profile = None
        self._profileDefault = None

    @property
    def env(self):
        return self.executor.env

    @property
    def home(self):
        return self.executor.cuisine.core.dir_paths["HOMEDIR"]

    def cmdGetPath(self, cmd, die=True):
        """
        checks cmd Exists and returns the path
        """
        rc, out, err = self.cuisine.core.run("which %s" % cmd, die=False, showout=False, profile=True)
        if rc > 0:
            if die:
                raise j.exceptions.RuntimeError("Did not find command: %s" % cmd)
            else:
                return False
        return out.split("\n")[-1]

    def profileGet(self, path="~/.profile_js"):
        path = path.replace("~", self.home)
        if not self.cuisine.core.file_exists(path):
            self.cuisine.core.file_write(path, "")
        return Profile(self, path)

    @property
    def profileJS(self):
        """
        profile which we write for jumpscale std in ~/.profile_js
        """
        if self._profile is None:
            self._profile = self.profileGet()
        return self._profile

    @property
    def profileDefault(self):
        if self._profileDefault is None:
            path = ""
            for attempt in [".profile", ".bash_profile"]:
                ppath = j.sal.fs.joinPaths(self.home, attempt)
                if self.cuisine.core.file_exists(ppath):
                    path = ppath
            if path == "":
                path = "~/.bash_profile"
            self._profileDefault = self.profileGet(path)
        return self._profileDefault

    @property
    def profilePath(self):
        return self.profileDefault.pathProfile

    def fixlocale(self):
        self.cuisine.bash.profileJS.fixlocale()
        self.cuisine.bash.profileJS.save(True)  # will make sure it gets in default profile

    def envSet(self, key, val):
        self.cuisine.bash.profileJS.envSet(key, val)
        self.cuisine.bash.profileJS.save(True)

    def envGet(self, key):
        return self.cuisine.bash.profileJS.envGet(key)

    def envDelete(self, key):
        return self.cuisine.bash.profileJS.envDelete(key)
