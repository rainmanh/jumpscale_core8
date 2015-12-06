
import sys
import os
import socket


if sys.platform.startswith("darwin"):
    os.environ['JSBASE']='/Users/Shared/jumpscale/'
    if not 'APPDATA' in os.environ:
        os.environ['APPDATA']='/Users/Shared/jumpscale/var'
    if not 'TMP' in os.environ:
        os.environ['TMP']=  os.environ['TMPDIR']+"jumpscale/"

    for p in ["/Users/Shared/jumpscale/lib","/Users/Shared/jumpscale/lib/lib-dynload/","/Users/Shared/jumpscale/bin","/Users/Shared/jumpscale/lib/python.zip","/Users/Shared/jumpscale/lib/plat-x86_64-linux-gnu"]:
        if p not in sys.path:
            sys.path.append(p)
    basevar="/Users/Shared/jumpscalevar"

if 'VIRTUAL_ENV' in os.environ and not 'JSBASE' in os.environ:
    os.environ['JSBASE'] = os.environ['VIRTUAL_ENV']
    base="/opt/jumpscale8"
    basevar="/optvar"
elif 'JSBASE' in os.environ:
    base=os.environ['JSBASE']
    basevar="/optvar"
else:
    base="/opt/jumpscale8"
    basevar="/optvar"


sys.path.insert(0,"/opt/jumpscale8/lib")


class Loader(object):
    def __init__(self):
        self._extensions = {}
        self.__members__ = []

    def _register(self, name, callback):
        # print ("register:%s"%name)
        self._extensions[name] = callback
        self.__members__.append(name)

    def __getattr__(self, attr):
        if attr not in self._extensions:
            raise AttributeError("%s is not loaded, did your forget an import?" % attr)
        obj = self._extensions[attr]()
        setattr(self, attr, obj)
        return obj

    def __dir__(self):
        first_list=object.__dir__(self)
        resulting_list = first_list + [i for i in self.__members__ if i not in first_list]
        return resulting_list

class JumpScale(Loader):
    pass

class Core(Loader):
    pass

# class System(Loader):
#     pass

# class SystemFS(Loader):
    # pass

class Sal(Loader):
    pass

class Data(Loader):
    pass

class Serializer(Loader):
    pass

class Tools(Loader):
    pass

class Types(Loader):
    pass


class Clients(Loader):
    pass

class Servers(Loader):
    pass

class EventsTemp():
    def inputerror_critical(self,msg,category=""):
        print(("ERROR IN BOOTSTRAP:%s"%category))
        print(msg)
        sys.exit(1)

def loadSubModules(filepath, prefix='JumpScale'):
    rootfolder = os.path.dirname(filepath)
    for module in os.listdir(rootfolder):
        if module.startswith("_"):
            # print ("SKIP_:%s"%(os.path.join(rootfolder, module)))
            continue
        moduleload = '%s.%s' % (prefix, module)
        if not os.path.isdir(os.path.join(rootfolder, module)):
            # print ("SKIP:%s"%(os.path.join(rootfolder, module)))
            continue
        try:
            __import__(moduleload, locals(), globals())
            # print ("imported:%s"%moduleload)
        except ImportError as e:
            # print ("COULD NOT IMPORT:%s \n%s"%(moduleload,e))
            pass

j = JumpScale()


j.data=Data()
j.data.serializer=Serializer()
j.clients=Clients()
j.tools=Tools()
j.core=Core()
j.core.types=Types()
j.sal=Sal()
# j.system=System()
# j.system.fs=SystemFS()
j.servers=Servers()

j.core.redis=None
# j.core.statsdb=None
# j.core.realitydb=None

j.events=EventsTemp()

from .InstallTools import InstallTools
from .InstallTools import Installer
j.do=InstallTools()
j.do.installer=Installer()

from . import core

from .core.PlatformTypes import PlatformTypes

j.core.platformtype=PlatformTypes()

# from .core import pmtypes
# pmtypes.register_types()
# j.basetype=pmtypes.register_types()

# from .core.Console import Console
# j.console=Console()

sys.path.append('/opt/jumpscale8/lib/JumpScale')

loadSubModules(__file__)

import core.types

j.application.config = j.data.hrd.get(path="%s/hrd/system"%basevar)

j.logger.enabled = j.application.config.getBool("system.logging",default=False)

from .core.Dirs import Dirs
j.dirs=Dirs()

from .core import errorhandling



j.application.init()



