
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

        self.base = j.do.BASE
        self.HOMEDIR = os.environ["HOME"]
        self.JSCFGDIR = os.environ["CFGDIR"]
        self.TMPDIR = os.environ["TMPDIR"]

    def normalize(self, path):
        """
        """
        if path:
            if "~" in path:
                path = path.replace("~", j.dirs.HOMEDIR)
            path = j.sal.fs.pathDirClean(path)
        return path

    def init(self):
        self.JSAPPDIR = self.normalize(j.sal.fs.joinPaths(self.base, "apps"))
        self.VARDIR = self.normalize(j.do.VARDIR)
        self.TEMPLATEDIR = self.normalize(j.sal.fs.joinPaths(self.base, "templates"))
        self.LIBDIR = j.sal.fs.joinPaths(self.base, 'lib')
        self.LOGDIR = self.normalize(j.sal.fs.joinPaths(self.VARDIR, "log"))
        self.PIDDIR = self.normalize(j.sal.fs.joinPaths(self.VARDIR, "pid"))
        self.CODEDIR = self.normalize(j.do.CODEDIR)
        self.libExtDir = j.sal.fs.joinPaths(self.base, 'libext')
        self.binDir = self.normalize(os.path.join(self.base, 'bin'))
        self.jsLibDir = os.path.join(self.LIBDIR, "JumpScale")

    def replaceTxtDirVars(self, txt, additionalArgs={}):
        """
        replace $BASEDIR,$vardir,$JSCFGDIR,$bindir,$codedir,$tmpdir,$logdir,$appdir with props of this class
        also the Dir... get replaces e.g. varDir
        """
        txt = txt.replace("$BASEDIR", self.base)
        txt = txt.replace("$appdir", self.JSAPPDIR)
        txt = txt.replace("$JSAPPDIR", self.JSAPPDIR)
        txt = txt.replace("$TEMPLATEDIR", self.TEMPLATEDIR)
        txt = txt.replace("$tmplsdir", self.TEMPLATEDIR)
        txt = txt.replace("$codedir", self.CODEDIR)
        txt = txt.replace("$CODEDIR", self.CODEDIR)
        txt = txt.replace("$vardir", self.VARDIR)
        txt = txt.replace("$VARDIR", self.VARDIR)
        txt = txt.replace("$cfgdir", self.JSCFGDIR)
        txt = txt.replace("$JSCFGDIR", self.JSCFGDIR)
        txt = txt.replace("$bindir", self.binDir)
        txt = txt.replace("$binDir", self.binDir)
        txt = txt.replace("$logdir", self.LOGDIR)
        txt = txt.replace("$LOGDIR", self.LOGDIR)
        txt = txt.replace("$tmpdir", self.TMPDIR)
        txt = txt.replace("$TMPDIR", self.TMPDIR)
        txt = txt.replace("$libdir", self.LIBDIR)
        txt = txt.replace("$LIBDIR", self.LIBDIR)
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
        out = ""
        for key, value in self.__dict__.items():
            if key[0] == "_":
                continue
            out += "%-20s : %s\n" % (key, value)
        out = j.data.text.sort(out)
        return out

    __repr__ = __str__
