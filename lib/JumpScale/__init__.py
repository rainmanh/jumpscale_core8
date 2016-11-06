import sys
import os
# import socket
# import time
import json
import argparse
import importlib
import importlib.machinery
import os.path
import locale
locale.setlocale(locale.LC_ALL, 'en_US.UTF-8')


from .InstallTools import InstallTools, do, Installer

# INITIALIZATION OF PATHS IS IN THE INSTALLTOOLS FILE, LETS ONLY DO THERE !!!

base = do.BASE
libMetadataPath = "%s/libMetadata.db" % do.CFGDIR

if not do.embed:
    from JumpScale.clients.redis.RedisFactory import RedisFactory

    if not os.path.isfile("%s/lib/lsb_release.py" % base):
        sys.path.insert(0, "%s/lib" % base)
        sys.path.insert(0, "%s/bin" % base)
        sys.path.insert(0, "%s/lib/JumpScale" % base)
        sys.path.insert(0, "%s/lib/lib-dynload" % base)

else:
    sys.path = []
    sys.path.insert(0, "%s/lib" % base)
    sys.path.insert(1, base)
    sys.path.insert(0, "%s/lib/base_library.zip" % base)
    sys.path.insert(0, "%s/lib/base.zip" % base)
    # sys.path.insert(0, "%s/binlib/")


libDir = "%s/lib" % base
libExtDir = "%s/libext" % base

pythonzip = '%s/python.zip' % libDir
if pythonzip in sys.path:
    sys.path.pop(sys.path.index(pythonzip))
if os.path.exists(pythonzip):
    sys.path.insert(0, pythonzip)

if libExtDir in sys.path:
    sys.path.pop(sys.path.index(libExtDir))
if os.path.exists(libExtDir):
    sys.path.insert(2, libExtDir)

jsLibDir = os.path.join(libDir, "JumpScale")
if jsLibDir in sys.path:
    sys.path.pop(sys.path.index(jsLibDir))
sys.path.insert(0, jsLibDir)


class Loader:

    def __init__(self, name):
        self.__doc__ = name
        locationbases[name] = self
        self._extensions = {}
        self.__members__ = []

    def _register(self, name, classfile, classname):
        # print ("%s   register:%s"%(self.__doc__,name))
        self._extensions[name] = (classfile, classname)
        self.__members__.append(name)

    def __getattr__(self, attr):
        if attr not in self._extensions:
            raise AttributeError(
                "%s.%s is not loaded, BUG, needs to be registered in init of jumpscale?" % (self.__doc__, attr))
        classfile, classname = self._extensions[attr]
        modpath = j.do.getDirName(classfile)
        sys.path.append(modpath)
        obj0 = importlib.machinery.SourceFileLoader(
            classname, classfile).load_module()
        obj = eval("obj0.%s()" % classname)
        sys.path.pop(sys.path.index(modpath))

        setattr(self, attr, obj)
        return obj

    def __dir__(self):
        first_list = object.__dir__(self)
        resulting_list = first_list + \
            [i for i in self.__members__ if i not in first_list]
        return resulting_list

    def __str__(self):
        return "loader: %s" % self.__doc__

    __repr__ = __str__

# For auto completion  #TODO: what is this, please tell Kristof
# if not all(x for x in range(10)):
locationbases = {}
j = Loader("j")
j.data = Loader("j.data")
j.data.serializer = Loader("j.data.serializer")
j.data.units = Loader('j.data.units')
j.data.models = Loader('j.data.models')
j.core = Loader("j.core")
j.sal = Loader("j.sal")
j.tools = Loader("j.tools")
j.clients = Loader("j.clients")
# j.clients.redis = Loader("j.clients.redis")
j.servers = Loader("j.servers")
j.portal = Loader('j.portal')
j.portal.tools = Loader('j.portal.tools')
j.legacy = Loader("j.legacy")


j.do = do
j.do.installer = Installer()
j.do.installer.do=do

# sets up the exception handlers for init
from . import core

if not do.embed:
    sys.path.append('%s/lib/JumpScale' % do.BASE)

# import importlib


def findjumpscalelocations(path):
    res = []
    C = j.do.readFile(path)
    classname = None
    for line in C.split("\n"):
        if line.startswith("class "):
            classname = line.replace("class ", "").split(
                ":")[0].split("(", 1)[0].strip()
        if line.find("self.__jslocation__") != -1:
            if classname is None:
                raise RuntimeError(
                    "Could not find class in %s while loading jumpscale lib." % path)
            location = line.split("=", 1)[1].replace(
                "\"", "").replace("'", "").strip()
            if location.find("self.__jslocation__") == -1:
                res.append((classname, location))
    return res


# import json


def findModules(embed=False):

    result = {}
    superroot = "%s/lib/JumpScale" % j.do.BASE

    print("FINDMODULES in %s" % superroot)
    for rootfolder in j.do.listDirsInDir(superroot, False, True):
        fullpath0 = os.path.join(superroot, rootfolder)
        if rootfolder.startswith("_"):
            continue
        for module in j.do.listDirsInDir(fullpath0, False, True):
            fullpath = os.path.join(superroot, rootfolder, module)
            if module.startswith("_"):
                continue

            for classfile in j.do.listFilesInDir(fullpath, False, "*.py"):
                basename = j.do.getBaseName(classfile)
                if basename.startswith("_"):
                    continue
                # look for files starting with Capital
                if str(basename[0]) != str(basename[0].upper()):
                    continue

                for (classname, location) in findjumpscalelocations(classfile):
                    if classname is not None:
                        loc = ".".join(location.split(".")[:-1])
                        item = location.split(".")[-1]
                        if loc not in result:
                            result[loc] = []
                        result[loc].append((classfile, classname, item))

    j.do.writeFile(libMetadataPath, json.dumps(result))


# LOAD metadata for libs
if not j.do.exists(path=libMetadataPath):
    findModules()
data = j.do.readFile(libMetadataPath)
locations = json.loads(data)

for locationbase, llist in locations.items():  # locationbase is e.g. j.sal
    loader = locationbases[locationbase]
    for classfile, classname, item in llist:
        loader._register(item, classfile, classname)

if not do.embed:
    j.clients.redis.init4jscore(j, do.TMPDIR)
else:
    j.core.db = None

parser = argparse.ArgumentParser(add_help=False)
parser.add_argument('-q', '--quiet', default=False,
                    action='store_true', help="Turn down logging")
options, args = parser.parse_known_args()
j.logger.set_quiet(options.quiet)
j.application.init()
