
import sys
import os
import socket
import time


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


# class Loader(object):
#     def __init__(self):
#         self._extensions = {}
#         self.__members__ = []

#     def _register(self, name, callback):
#         # print ("register:%s"%name)
#         self._extensions[name] = callback
#         self.__members__.append(name)

#     def __getattr__(self, attr):
#         print (self._extensions)
#         if attr not in self._extensions:
#             raise AttributeError("%s is not loaded, did your forget an import?" % attr)
#         obj = self._extensions[attr]()
#         setattr(self, attr, obj)
#         return obj

#     def __dir__(self):
#         first_list=object.__dir__(self)
#         resulting_list = first_list + [i for i in self.__members__ if i not in first_list]
#         return resulting_list

class JumpScale():
    pass

    # def __init__(self):
    #     # self._sal=None
    #     pass

    # def _listLibDirs(self):
    #     pass

    # @property
    # def sal(self):
    #     path="sal2"
    #     if self._sal==None:
    #         jj=j.core.db.get("system.serialized.sal")
    #         self._sal=pickle.loads(jj)
    #     return self._sal





class EventsTemp():
    def inputerror_critical(self,msg,category=""):
        print(("ERROR IN BOOTSTRAP:%s"%category))
        print(msg)
        sys.exit(1)

# def loadSubModules(filepath, prefix='JumpScale'):
#     rootfolder = os.path.dirname(filepath)
#     for module in os.listdir(rootfolder):
#         if module.startswith("_"):
#             # print ("SKIP_:%s"%(os.path.join(rootfolder, module)))
#             continue
#         moduleload = '%s.%s' % (prefix, module)
#         if not os.path.isdir(os.path.join(rootfolder, module)):
#             # print ("SKIP:%s"%(os.path.join(rootfolder, module)))
#             continue
#         try:
#             __import__(moduleload, locals(), globals())
#             # print ("imported:%s"%moduleload)
#         except ImportError as e:
#             # print ("COULD NOT IMPORT:%s \n%s"%(moduleload,e))
#             pass



j = JumpScale()

# j.data.serializer=Serializer()
# j.core.types=Types()

j.events=EventsTemp()

print (1)
from .InstallTools import InstallTools
from .InstallTools import Installer
j.do=InstallTools()
j.do.installer=Installer()

from . import core

from .core.PlatformTypes import PlatformTypes

class Loader(object):
    def __init__(self,):
        self._extensions = {}
        self.__members__ = []

    def _register(self, name,classfile,classname):
        # print ("register:%s"%name)
        self._extensions[name] = (classfile,classname)
        self.__members__.append(name)

    def __getattr__(self, attr):
        if attr not in self._extensions:
            raise AttributeError("%s is not loaded, did your forget an import?" % attr)

        classfile,classname=self._extensions[attr]
        modpath=j.do.getDirName(classfile)
        sys.path.append(modpath)
        obj0 = importlib.machinery.SourceFileLoader(classname,classfile).load_module()
        obj=eval("obj0.%s()"%classname)
        sys.path.pop(sys.path.index(modpath))

        setattr(self, attr, obj)
        return obj

    def __dir__(self):
        first_list=object.__dir__(self)
        resulting_list = first_list + [i for i in self.__members__ if i not in first_list]
        return resulting_list



class Core(Loader):
    pass

class Data(Loader):
    pass

class Types():
    pass

j.data=Data()
j.core=Core()
j.core.types=Types()

j.core.platformtype=PlatformTypes()


sys.path.append('/opt/jumpscale8/lib/JumpScale')

import importlib




def redisinit():
    import redis
    if not os.path.exists('/tmp/redis.sock'):
        open('/tmp/redis.sock', 'a').close()
    j.core.db=redis.Redis(unix_socket_path='/tmp/redis.sock')
    try:
        j.core.db.set("internal.last",0)
    except:
        print ("warning:did not find redis")
        j.core.db=None

import os
redisinit()
if j.core.db==None:
    url="http://stor.jumpscale.org:8000/public/redis-server"
    j.do.download(url, to='/opt/jumpscale8/bin/redis', overwrite=False, retry=3)
    import subprocess
    cmd="chmod 550 /opt/jumpscale8/bin/redis;/opt/jumpscale8/bin/redis --unixsocket /tmp/redis.sock --maxmemory 100000000 --daemonize yes"
    print ("start redis in background")
    os.system(cmd)
    # Wait until redis is up
    redisinit()
    while j.core.db==None:
        redisinit()
        time.sleep(1)


def findjumpscalelocation(path):
    C=j.do.readFile(path)
    for line in C.split("\n"):
        if line.startswith("class "):
            classname=line.replace("class ","").split(":")[0].split("(",1)[0].strip()
        if line.find("self.__jslocation__")!=-1:
            location=line.split("=",1)[1].replace("\"","").replace("'","").strip()
            return classname,location
    return None,None

import json

def findModules():
    result={}
    superroot = j.do.getDirName(__file__)
    for rootfolder in j.do.listDirsInDir(superroot,False,True):
        fullpath0=os.path.join(superroot,superroot, rootfolder)
        if rootfolder.startswith("_"):
            # print ("SKIP__:%s"%fullpath0)
            continue
        for module in j.do.listDirsInDir(fullpath0,False,True):
            fullpath=os.path.join(superroot,rootfolder, module)
            if module.startswith("_"):
                # print ("SKIP_:%s"%fullpath)
                continue
            # moduleload = '%s.%s' % (prefix, module)

            for classfile in j.do.listFilesInDir(fullpath,False,"*.py"):
                basename=j.do.getBaseName(classfile)
                if basename.startswith("_"):
                    # print ("SKIP_file:%s (%s)"%(classfile,basename))
                    continue
                if str(basename[0])!=str(basename[0].upper()):#look for files starting with Capital
                    # print ("SKIP_file_upper:%s (%s)"%(classfile,basename))
                    continue

                classname,location=findjumpscalelocation(classfile)

                if classname!=None:
                    print ("location:%s"%location)
                    loc=".".join(location.split(".")[:-1])
                    item=location.split(".")[-1]
                    if loc not in result:
                        result[loc]=[]
                    result[loc].append((classfile,classname,item))
                    #load the class, bytecompiled & remember in redis
    j.core.db.set("system.locations",json.dumps(result))

if j.core.db.get("system.locations")==None:
    res=findModules()

locations=json.loads(j.core.db.get("system.locations").decode())

buildup={}
buildup["j.core"]=j.core
buildup["j.data"]=j.data
for location,llist in locations.items():
    if location not in buildup:
        # for classfile,classname,item in llist:
        # loader=Loader()
        classname0=location.split(".")[-1]
        if classname0 not in ["core","data"]:
            cmd="class %s_(Loader):\n    pass\n%s=%s_()\nbuildup[\"%s\"]=%s"%(classname0,location,classname0,location,location)
            print (cmd)
            exec(cmd)
    print("location:%s"%location)
    loader=buildup[location]
    for classfile,classname,item in llist:
        loader._register(item,classfile,classname)

print (locations)

import core.types

from IPython import embed
embed()

j.application.config = j.data.hrd.get(path="%s/hrd/system"%basevar)

j.logger.enabled = j.application.config.getBool("system.logging",default=False)

from .core.Dirs import Dirs
j.dirs=Dirs()

from .core import errorhandling


print (2)
j.application.init()
print (3)
