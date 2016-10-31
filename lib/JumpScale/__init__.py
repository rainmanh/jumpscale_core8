def embed():
    return "embed" in sys.__dict__

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


if not embed():
    from JumpScale.clients.redis.RedisFactory import RedisFactory

    if sys.platform.startswith("darwin") or sys.platform.startswith("cygwin"):

        base = "%s/opt/jumpscale8" % os.environ["HOME"]
        basevar = "%s/optvar" % os.environ["HOME"]

        # os.environ['JSBASE']='/Users/Shared/jumpscale/'
        if not 'APPDATA' in os.environ:
            os.environ['APPDATA'] = basevar
        if not 'TMP' in os.environ:
            os.environ['TMP'] = os.environ['TMPDIR'] + "jumpscale/"

        # for p in ["%s/lib"%base,"%s/lib/lib-dynload/"%base,"%s/bin"%base,"%s/lib/plat-x86_64-linux-gnu"%base]:
        #     if p not in sys.path:
        #         sys.path.append(p)

        os.environ["TMP"] = os.path.join(os.environ["HOME"], "tmp")

    else:
        if "JSBASE" not in os.environ:
            os.environ["JSBASE"] = "/opt/jumpscale8"
            # raise j.exceptions.RuntimeError("Cannot load jumpscale, please specify JSBASE as env variable.")
        base = os.environ["JSBASE"]
        basevar = "/optvar"

        os.environ["TMP"] = os.path.join(basevar, "tmp")

    tmpdir = os.environ["TMP"]
    if not os.path.isdir(tmpdir):
        os.makedirs(tmpdir)
    os.environ['TMP'] = tmpdir

    if not os.path.isfile("%s/lib/lsb_release.py" % base):
        sys.path.insert(0, "%s/lib" % base)
        sys.path.insert(0, "%s/bin" % base)
        sys.path.insert(0, "%s/lib/JumpScale" % base)
        sys.path.insert(0, "%s/lib/lib-dynload" % base)

    else:
        # print ("sandbox")
        sys.path = []
        sys.path.append("%s/lib" % base)
        sys.path.append("%s/bin" % base)
        sys.path.append("%s/lib/JumpScale" % base)
        sys.path.append("%s/lib/lib-dynload" % base)
else:
    basevar = "%s/optvar" % os.environ["HOME"]
    os.environ['TMP'] = os.environ['TMPDIR'] + "jumpscale/tmp/"
    os.environ['APPDATA'] = os.environ['TMPDIR'] + "jumpscale/appdata/"
    os.environ["JSBASE"] = os.environ['TMPDIR'] + "jumpscale/base/"
    sys.path = []
    base = os.getcwd()
    sys.path.insert(0, "%s/lib" % base)
    sys.path.insert(1, base)
    sys.path.insert(0, "%s/lib/base_library.zip"%base)
    sys.path.insert(0, "%s/lib/base.zip"%base)
    # sys.path.insert(0, "%s/binlib/")
    os.makedirs(os.environ["TMP"], exist_ok=True)
    os.makedirs(os.environ["APPDATA"], exist_ok=True)
    os.makedirs(os.environ["JSBASE"], exist_ok=True)


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
if not embed():
    j.clients.redis = RedisFactory()
j.servers = Loader("j.servers")
j.portal = Loader('j.portal')
j.portal.tools = Loader('j.portal.tools')
j.legacy = Loader("j.legacy")

from .InstallTools import InstallTools, do, Installer
j.do = do
j.do.installer = Installer()

# sets up the exception handlers for init
from . import core

if not embed():
    sys.path.append('%s/lib/JumpScale' % j.do.BASE)

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


if not embed():
    j.clients.redis.init4jscore(j, tmpdir)


# import json


def findModules(embed=False):

    result = {}
    if embed:
        superroot = "%s/lib/JumpScale" % os.getcwd()
    else:
        if os.path.isdir(j.do.BASE):
            superroot = "%s/lib/JumpScale" % j.do.BASE
        else:
            if j.core.db.get("system.superroot") is None:
                superroot = j.do.getDirName(__file__)
                j.core.db.set("system.superroot", superroot)
            superroot = j.core.db.get("system.superroot").decode()

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

    if not embed:
        j.core.db.set("system.locations", json.dumps(result))
        if base == "/opt/jumpscale8/":
            j.do.writeFile("%s/metadata.db" % j.do.VARDIR, json.dumps(result))
    else:
        j.do.writeFile("%s/metadata.db" % base, json.dumps(result))


forcereload = False

if not embed():

    if base != "/opt/jumpscale8/":
        mdpath = "%s/metadata.db" % j.do.VARDIR
        if j.do.exists(mdpath):
            forcereload = True
            j.do.delete(mdpath)
            # make sure redis is empty
            if j.core.db is not None:
                j.core.db.flushall()
            if base == "/optrw/jumpscale8":
                j.do.installer.writeenv(
                    basedir=base, insystem=False, CODEDIR='/optrw/code')
            print("force metadata reload")

    data = j.core.db.get("system.locations")
    if forcereload or data is None:
        if not j.do.exists(path="%s/metadata.db" % j.do.VARDIR):
            print("RELOAD LIB METADATA")
            res = findModules()
            data = j.core.db.get("system.locations").decode()
        else:
            data = j.do.readFile("%s/metadata.db" % j.do.VARDIR)
    else:
        data = data.decode()
else:
    if not j.do.exists(path="%s/metadata.db" % base):
        findModules(True)

    data = j.do.readFile("%s/metadata.db" % base)

locations = json.loads(data)
for locationbase, llist in locations.items():  # locationbase is e.g. j.sal
    loader = locationbases[locationbase]
    for classfile, classname, item in llist:
        loader._register(item, classfile, classname)

if not j.do.exists("%s/hrd/system/system.hrd" % basevar):
    j.do.installer.writeenv(die=False)

if not embed():
    data = j.core.db.get("system.dirs.%s" % j.do.BASE)
    if data is None:
        j.application._config = j.data.hrd.get(path="%s/hrd/system" % basevar)
else:
    j.core.db = None

parser = argparse.ArgumentParser(add_help=False)
parser.add_argument('-q', '--quiet', default=False,
                    action='store_true', help="Turn down logging")
options, args = parser.parse_known_args()
j.logger.set_quiet(options.quiet)
j.application.init()
