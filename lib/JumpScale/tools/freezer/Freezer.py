from JumpScale import j

JS = """

print(111)
print (sys.path)

import sys
import os
home = os.environ["HOME"]
if not os.path.exists("%s/JS8" % home):
    raise RuntimeError("Cannot start jumpscale, need sandboxed ~/JS8 dir")

toremove = []
for item in sys.path:
    if item.find("jumpscale") != -1:
        toremove.append(item)
    if item.find("python") != -1:
        toremove.append(item)


for item in toremove:
    sys.path.pop(sys.path.index(item))

sys.path.append("%s/JS8/opt/jumpscale8/lib" % home)
sys.path.append("%s/JS8/opt/jumpscale8/bin" % home)
sys.path.append("%s/JS8/opt/jumpscale8/bin/base_library.zip" % home)
sys.path.append("%s/JS8/opt/jumpscale8/lib/baselibs" % home)
sys.path.append("%s/JS8/opt/jumpscale8/lib/baselibs.zip" % home)

print (sys.path)

# import tarfile
# import shutil
# import tempfile
# import platform
# import subprocess
# import time
# import fnmatch
# from subprocess import Popen
# import re
# import inspect
# import yaml
# import importlib
# import asyncio
# if sys.platform != 'cygwin':
#     import uvloop

# from urllib.request import urlopen


from JumpScale import j

import argparse
j.application.start("jsshell")

parser = argparse.ArgumentParser()
parser.add_argument('-q', '--quiet', default=False, action='store_true', help="Turn down logging")
options, args = parser.parse_known_args()


import sys
if len(args) == 1:
    toexec = args[0]
    toexec = toexec.strip("'\\" ").strip("'\\" ")
    exec(toexec)
else:
    from IPython import embed
    embed(colors='Linux')

    j.application.stop()
"""


class Freezer:
    """
    free python apps to executables
    """

    def __init__(self):
        self.__jslocation__ = "j.tools.freezer"
        self.jsbase = j.sal.fs.joinPaths(j.dirs.HOMEDIR, "JS8")

    def install(self):
        cmd = "pip3 install --upgrade pyinstaller"
        rc, out = j.sal.process.execute(cmd, die=True, showout=True, ignoreErrorOutput=False)

    def cleanSystem(self, backup=True):
        if not str(j.core.platformtype.myplatform).startswith("darwin"):
            raise j.exceptions.Input(message="only support osx for now", level=1, source="", tags="", msgpub="")
        if backup:
            backupdir = j.sal.fs.joinPaths(j.dirs.HOMEDIR, "_backup")
            j.sal.fs.createDir(backupdir)
        else:
            backupdir = ""

        def move(path, filter="*", backupdir=""):
            if j.sal.fs.isFile(path):
                items = [path]
            elif j.sal.fs.isDir(path) and filter == "":
                dest = "%s/%s" % (backupdir, path)
                dest = dest.replace("//", "/")
                j.sal.process.execute("rsync -ra %s/ %s/" % (path, dest))
                j.sal.process.execute("rm -rf %s/" % (path))

            else:
                items = j.sal.fs.listFilesAndDirsInDir(path, recursive=True, filter=filter, minmtime=None,
                                                       maxmtime=None, depth=None, type="fd",
                                                       followSymlinks=False, listSymlinks=True)
            for item in items:
                item = j.sal.fs.joinPaths(path, item)
                if backupdir != "":
                    dest = "%s/%s" % (backupdir, item)
                    dest = dest.replace("//", "/")
                    j.sal.fs.createDir(j.sal.fs.getDirName(dest))
                    if j.sal.fs.isFile(item):
                        j.sal.fs.copyFile(item, dest)
                        if j.sal.fs.isLink(item):
                            src = j.sal.fs.readlink(item)
                            move(src, backupdir=backupdir)
                    elif j.sal.fs.isDir(item):
                        # the find will find underlying files, so nothing to do
                        pass
                        # j.sal.fs.copyDirTree(item, dest, keepsymlinks=True)
                if j.sal.fs.isFile(item):
                    j.sal.fs.remove(item)

        # NOT WORKING BECAUSE OF STUPID RESTRICTIONS OSX, so lets ignore for now
        # move("/usr/bin", "pyth*", backupdir=backupdir)
        # move("/usr/bin", "pydoc*", backupdir=backupdir)

    def addPythonLib(path):
        """
        path isn the location where libs can be found
        """
        exclude = ["cython", ".dist-info", ".egg-info"]
        include = ["flask", "fxrays", "ipython", "jinja", "mako", "markupsafe", "openssl", "pil",
                   "pillow", "git", "jwt", "yaml",
                   "pygments", "forms", "werkzeug", "redis", "tarantool", "gogs",
                   "nope", "argcompl", "argh", "ascii", "pep", "backport", "async",
                   "bcrypt", "beaker", "blinker", "blosc", "bson",
                   "capnp", "colorama", "log", "cerberus", "capturer", "cffi",
                   "click", "traceback", "cson", "date", "dns", "decorator",
                   "doc", "utils", "dulwich", "ecdsa", "dominate", "eve", "falkon", "flake", "buffers", "flex",
                   "future", "gevent", "readline", "html", "infi", "marisa",
                   "xml", "markup", "markdown", "mime", "mongo", "msgpack", "mustache",
                   "network", "pass", "past", "path", "peewee", "pip", "plink",
                   "ply", "posix", "protobuf", "prompt", "pkg", "pexpect", "paramiko",
                   "psycop", "process", "pudb", "pyasn", "blake", "parser", "docstyle",
                   "pyfiglet", "pygments", "lzma", "lru", "mustache", "mux", "stache",
                   "png", "dateutil", "snappy", "telegram", "mmap", "request",
                   "pytz", "pyte", "toml", "import", "json", "snakeviz", "pool",
                   "tornado", "traitlets", "url", "uvloop", "visitor", "watchdog",
                   "wheel"]

        def match(txt, listInclude=[], listExclude=[]):
            txt = txt.lower()
            for item in listInclude:
                if txt.find(item) != -1:
                    excl = False
                    for itemExcl in listExclude:
                        if txt.find(itemExcl) != -1:
                            excl = True
                    if not excl:
                        return True
            return False

        for item in j.sal.fs.listDirsInDir(path, dirNameOnly=True, recursive=False):
            if match(item, include, exclude):
                src = j.sal.fs.joinPaths(path, item)
                dest = j.sal.fs.joinPaths(self.jsbase, "lib", "baselib", item)
                print(dest)
                j.sal.fs.copyDirTree(src, dest, keepsymlinks=False, deletefirst=True, overwriteFiles=True, ignoredir=['.egg-info', '.dist-info'], ignorefiles=[
                                     '.egg-info'], rsync=True, recursive=True, rsyncdelete=True, createdir=True)

        for item in j.sal.fs.listFilesInDir(path, filter="*.so", recursive=False):
            dest = j.sal.fs.joinPaths(jsbase, "lib", "baselib", j.sal.fs.getBaseName(item))
            j.sal.fs.copyFile(item, dest)

        for item in j.sal.fs.listFilesInDir(path, filter="*.py", recursive=False):
            dest = j.sal.fs.joinPaths(jsbase, "opt", "jumpscale8", "lib", "baselib", j.sal.fs.getBaseName(item))
            j.sal.fs.copyFile(item, dest)

        dest = j.sal.fs.joinPaths(jsbase, "opt", "jumpscale8", "lib", "baselib")

        cmd = "chown -R $USER %s" % (jsbase)
        j.sal.process.executeWithoutPipe(cmd)

        for item in j.sal.fs.listFilesInDir(dest, filter="*.pyc", recursive=True):
            j.sal.fs.remove(item)

        for item in j.sal.fs.listDirsInDir(dest, recursive=True, dirNameOnly=False, findDirectorySymlinks=True):
            if item.find("__pycache__") != -1:
                j.sal.fs.remove(item)

    def do(self, reset=False):

        if reset:
            j.sal.fs.removeDirTree(jsbase)
        j.sal.fs.createDir(jsbase)

        def copy(jsbase, path):
            path = path.rstrip("/")
            dest = path.lstrip("/")
            if dest.startswith("JS8"):
                dest = dest[4:]
                dest = j.sal.fs.joinPaths(jsbase, dest)
                dest = dest.rstrip("/")
            else:
                raise j.exceptions.Input(message="wrong path", level=1, source="", tags="", msgpub="")

            cmd = 'rsync -raL %s/ %s/' % (path, dest)
            j.sal.fs.createDir(dest)
            print(cmd)
            rc, out = j.sal.process.execute(cmd, die=True, showout=False, ignoreErrorOutput=False)
        copy(jsbase, "/JS8/opt/jumpscale8/lib/JumpScale")
        copy(jsbase, "/JS8/opt/jumpscale8/templates")

        tmpdir = j.sal.fs.joinPaths(j.dirs.TMPDIR, "freezer")
        j.sal.fs.createDir(tmpdir)
        j.sal.fs.writeFile(filename=j.sal.fs.joinPaths(tmpdir, "js.py"), contents=JS, append=False)

        rc, out = j.sal.process.execute("which pyinstaller", die=False)
        if rc > 0:
            self.install()

        j.sal.fs.changeDir(tmpdir)

        # cmd = "rm js.spec;rm -rf build;rm -rf dist;pyinstaller js.py"
        # j.sal.process.executeWithoutPipe(cmd)
        # cmd = "rsync -raL dist/js/ %s/opt/jumpscale8/bin/" % jsbase
        # j.sal.process.executeWithoutPipe(cmd)

        pythonlib(jsbase, "/usr/local/lib/python3.5/site-packages")
