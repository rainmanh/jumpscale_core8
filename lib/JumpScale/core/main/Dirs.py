
import sys
import os
import inspect

from JumpScale import j


def embed():
    return "embed" in sys.__dict__


def pathToUnicode(path):
    """
    Convert path to unicode. Use the local filesystem encoding. Will return
    path unmodified if path already is unicode.

    @param path: path to convert to unicode
    @type path: basestring
    @return: unicode path
    @rtype: unicode
    """
    if isinstance(path, str):
        return path

    return path.decode(sys.getfilesystemencoding())


class Dirs:
    """Utility class to configure and store all relevant directory paths"""

    def __init__(self):
        '''jumpscale sandbox base folder'''
        self.__jslocation__ = "j.dirs"
        self.__initialized = False  # bool

        import sys

        # self.base=j.application.config.get("dirs.base")
        self.base = j.do.BASE
        self.homeDir = os.environ["HOME"]
        self.cfgDir = os.environ["CFGDIR"]
        self.tmpDir = os.environ["TMPDIR"]

    def normalize(self, path):
        """
        """
        if path:
            if "~" in path:
                path = path.replace("~", j.dirs.homeDir)
            path = j.sal.fs.pathDirClean(path)
        return path

    def init(self):
        print("load dirs")

        if not embed():
            self.appDir = self.normalize(j.application.config["dirs"].get('app'))
            self.tmplsDir = self.normalize(j.application.config["dirs"].get("templates"))
            self.varDir = self.normalize(j.application.config["dirs"].get("VARDIR"))
            self.cfgDir = self.normalize(j.application.config["dirs"].get("CFGDIR"))
            self.libDir = j.sal.fs.joinPaths(self.base, 'lib')
            self.logDir = self.normalize(j.application.config["dirs"].get("log"))
            self.pidDir = self.normalize(j.application.config["dirs"].get("pid"))
            self.codeDir = self.normalize(j.application.config["dirs"].get("CODEDIR"))
            self.libExtDir = self.normalize(j.application.config["dirs"].get("python.lib.ext"))
            self._createDir(self.tmplsDir)

            pythonzip = self.normalize(os.path.join(self.libDir, 'python.zip'))
            if os.path.exists(pythonzip):
                if pythonzip in sys.path:
                    sys.path.pop(sys.path.index(pythonzip))
                sys.path.insert(0, pythonzip)

            if self.libExtDir in sys.path:
                sys.path.pop(sys.path.index(self.libExtDir))
            sys.path.insert(2, self.libExtDir)

            if 'JSBASE' in os.environ:
                self.binDir = self.normalize(os.path.join(self.base, 'bin'))
            else:
                self.binDir = self.normalize(j.application.config.get("dirs.bin"))

            data = j.data.serializer.json.dumps(self.__dict__)
            j.core.db.set("system.dirs.%s" % self.base, data)

            self._createDir(os.path.join(self.base, "libext"))

        else:
            self.appDir = os.getcwd()
            self.varDir = os.environ['APPDATA']
            self.cfgDir = "%s/cfg" % self.appDir
            self.libDir = self.appDir
            self.logDir = "%s/log" % self.tmpDir
            self.pidDir = self.tmpDir
            self.codeDir = self.tmpDir
            self.libExtDir = ""

        self.jsLibDir = os.path.join(self.libDir, "JumpScale")

        if self.libDir in sys.path:
            sys.path.pop(sys.path.index(self.libDir))
        sys.path.insert(0, self.libDir)

    def replaceTxtDirVars(self, txt, additionalArgs={}):
        """
        replace $base,$vardir,$cfgDir,$bindir,$codedir,$tmpdir,$logdir,$appdir with props of this class
        also the Dir... get replaces e.g. varDir
        """
        txt = txt.replace("$base", self.base)
        txt = txt.replace("$appdir", self.appDir)
        txt = txt.replace("$appDir", self.appDir)
        txt = txt.replace("$tmplsDir", self.tmplsDir)
        txt = txt.replace("$tmplsdir", self.tmplsDir)
        txt = txt.replace("$codedir", self.codeDir)
        txt = txt.replace("$codeDir", self.codeDir)
        txt = txt.replace("$vardir", self.varDir)
        txt = txt.replace("$varDir", self.varDir)
        txt = txt.replace("$cfgdir", self.cfgDir)
        txt = txt.replace("$cfgDir", self.cfgDir)
        txt = txt.replace("$bindir", self.binDir)
        txt = txt.replace("$binDir", self.binDir)
        txt = txt.replace("$logdir", self.logDir)
        txt = txt.replace("$logDir", self.logDir)
        txt = txt.replace("$tmpdir", self.tmpDir)
        txt = txt.replace("$tmpDir", self.tmpDir)
        txt = txt.replace("$libdir", self.libDir)
        txt = txt.replace("$libDir", self.libDir)
        txt = txt.replace("$jslibextdir", self.libExtDir)
        txt = txt.replace("$jsbindir", self.binDir)
        txt = txt.replace("$nodeid", str(j.application.whoAmI.nid))
        # txt=txt.replace("$jumpscriptsdir", j.core.jumpscripts.basedir)
        for key, value in list(additionalArgs.items()):
            txt = txt.replace("$%s" % key, str(value))
        return txt

    def replaceFilesDirVars(self, path, recursive=True, filter=None, additionalArgs={}):
        if j.sal.fs.isFile(path):
            paths = [path]
        else:
            paths = j.sal.fs.listFilesInDir(path, recursive, filter)

        for path in paths:
            content = j.sal.fs.fileGetContents(path)
            content2 = self.replaceTxtDirVars(content, additionalArgs)
            if content2 != content:
                j.sal.fs.writeFile(filename=path, contents=content2)

    def _createDir(self, path):
        try:
            if not os.path.exists(path):
                os.makedirs(path)
        except:
            pass

    def _getParent(self, path):
        """
        Returns the parent of the path:
        /dir1/dir2/file_or_dir -> /dir1/dir2/
        /dir1/dir2/            -> /dir1/
        TODO: why do we have 2 implementations which are almost the same see getParentDirName()
        """
        parts = path.split(os.sep)
        if parts[-1] == '':
            parts = parts[:-1]
        parts = parts[:-1]
        if parts == ['']:
            return os.sep
        return os.sep.join(parts)

    def _getLibPath(self):
        parent = self._getParent
        libDir = parent(parent(__file__))
        libDir = os.path.abspath(libDir).rstrip("/")
        return libDir

    def getPathOfRunningFunction(self, function):
        return inspect.getfile(function)

    def __str__(self):
        return str(self.__dict__)  # TODO: P3 implement (thisnis not working)

    __repr__ = __str__
