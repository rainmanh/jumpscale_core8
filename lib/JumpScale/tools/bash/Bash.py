from JumpScale import j
import re
from io import StringIO
import os
from JumpScale.tools.cuisine.ActionDecorator import ActionDecorator


class actionrun(ActionDecorator):

    def __init__(self, *args, **kwargs):
        ActionDecorator.__init__(self, *args, **kwargs)
        self.selfobjCode = "cuisine=j.tools.cuisine.getFromId('$id');selfobj=cuisine.bash"


class Profile:
    env_pattern = re.compile(r'^([^=\n]+)="([^"\n]+)"$', re.MULTILINE)
    include_pattern = re.compile(r'^source (.*)$', re.MULTILINE)

    def __init__(self, content, binDir=None):
        """
        X="value"
        Y="value"
        PATH="p1:p2:p3"

        export X
        export Y
        """
        self._env = {}
        self._path = set()
        self._includes = set()
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
            # self._path.add('${PATH}')
            if binDir != None:
                _path.add(binDir)

        for item in _path:
            if item in [None, "${PATH}"]:
                continue
            if item.strip() == "":
                continue
            self.addPath(item)

        self._env.pop('PATH', None)

    def addPath(self, path):
        path = path.strip()
        path = path.replace("//", "/")
        path = path.replace("//", "/")
        path = path.rstrip("/")
        if not path in self._path:
            self._path.add(path)

    def addInclude(self, path):
        path = path.strip()
        path = path.replace("//", "/")
        path = path.replace("//", "/")
        path = path.rstrip("/")
        if not path in self._includes:
            self._includes.add(path)

    @property
    def path(self):
        return list(self._path)

    def set(self, key, value):
        self._env[key] = value

    def remove(self, key):
        del self._env[key]

    def dump(self):
        parts = ['${PATH}']
        parts.extend(self.path)
        self._env['PATH'] = ':'.join(set(self._path)) + ':${PATH}'

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

    @property
    def environ(self):
        return self._env


class Bash:

    def __init__(self):
        self.__jslocation__ = "j.tools.bash"
        self._profilePath = ""
        self._profile = None
        self._cuisine = j.tools.cuisine.get()
        self.executor = self._cuisine._executor
        self.reset()

    def get(self, cuisine, executor):
        b = Bash()
        b.cuisine = cuisine
        b.executor = executor
        return b

    def reset(self):
        self._environ = {}
        self._home = None
        self._profilePath = ""
        self._profile = None

    def replaceEnvironInText(self, text):
        """
        will look for $ENVIRONNAME 's and replace them in text
        """
        for key, val in self.environ.items():
            text = text.replace("$%s" % key, val)
        return text

    @property
    def environ(self):
        if self._environ == {}:
            res = {}
            for line in self._cuisine.core.run("printenv", profile=True, showout=False)[1].splitlines():
                if '=' in line:
                    name, val = line.split("=", 1)
                    name = name.strip()
                    val = val.strip().strip("'").strip("\"")
                    res[name] = val
            self._environ = res
        merge = self._environ.copy()
        merge.update(self.profile.environ)
        return merge

    @property
    def home(self):
        if not self._home:
            res = {}
            for line in self._cuisine.core.run("printenv", profile=False, showout=False)[1].splitlines():
                if '=' in line:
                    name, val = line.split("=", 1)
                    name = name.strip()
                    val = val.strip().strip("'").strip("\"")
                    res[name] = val
            self._home = res["HOME"]
        return self._home

    def environGet(self, name, default=None):
        """
        Get environ
        """
        return self.profile.environ.get(name, default)

    def environSet(self, key, val, temp=False):
        """
        Set environ
        """
        self._environ[key] = val
        os.environ[key] = val
        self.profile.set(key, val)
        self.write()
        self.reset()

    def setOurProfile(self):
        mpath = j.sal.fs.joinPaths(self.home, ".profile")
        mpath2 = j.sal.fs.joinPaths(self.home, ".profile_js")
        attempts = [mpath, j.sal.fs.joinPaths(self.home, ".bash_profile")]
        path = ""
        for attempt in attempts:
            if self._cuisine.core.file_exists(attempt):
                path = attempt

        if path == "":
            path = mpath
            self._cuisine.core.file_write(mpath, ". %s\n" % mpath2)
        else:
            out = self._cuisine.core.file_read(path)

            out = "\n".join(line for line in out.splitlines() if line.find("profile_js") == -1)

            out += "\n\n. %s\n" % mpath2

            self._cuisine.core.file_write(path, out)
        self.reset()
        return None

    def cmdGetPath(self, cmd, die=True):
        """
        checks cmd Exists and returns the path
        """
        rc, out, err = self._cuisine.core.run("which %s" % cmd, die=False, showout=False, profile=True)
        if rc > 0:
            if die:
                raise j.exceptions.RuntimeError("Did not find command: %s" % cmd)
            else:
                return False
        return out.split("\n")[-1]

    @property
    def profilePath(self):
        if self._profilePath == "":
            self._profilePath = j.sal.fs.joinPaths(self.home, ".profile_js")
        if not self._cuisine.core.file_exists(self._profilePath):
            self._cuisine.core.file_write(self._profilePath, self.profile.dump())
            self.setOurProfile()
            self._profile = None
        return self._profilePath

    @property
    def profile(self):
        if not self._profile:
            content = ""
            if self._profilePath == "" and self._cuisine.core.file_exists(self.profilePath):
                content = self._cuisine.core.file_read(self.profilePath)
            self._profile = Profile(content, self._cuisine.core.dir_paths["binDir"])

        return self._profile

    def addPath(self, path):
        self.profile.addPath(path)
        self.write()

    def write(self):
        self._cuisine.core.file_write(self.profilePath, self.profile.dump(), showout=False)

    def environRemove(self, key, val=None):
        self.profile.remove(key)
        self.write()

    def include(self, path):
        self.profile.addInclude(path)
        self.write()

    def getLocaleItems(self, force=False, showout=False):
        out = self._cuisine.core.run("locale -a")[1]
        return out.split("\n")

    def fixlocale(self):
        items = self.getLocaleItems()
        if "en_US.UTF-8" in items or "en_US.utf8" in items:
            self.environSet("LC_ALL", "en_US.UTF-8")
            self.environSet("LANG", "en_US.UTF-8")
            return
        elif "C.UTF-8" in items or "c.utf8" in items:
            self.environSet("LC_ALL", "C.UTF-8")
            self.environSet("LANG", "C.UTF-8")
            return

        raise j.exceptions.Input("Cannot find C.UTF-8, cannot fix locale's")
