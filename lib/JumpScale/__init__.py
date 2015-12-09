
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

class Loader(object):
    def __init__(self,name):
        self.__doc__=name
        locationbases[name]=self
        self._extensions = {}
        self.__members__ = []

    def _register(self, name,classfile,classname):
        print ("register:%s"%name)
        self._extensions[name] = (classfile,classname)
        self.__members__.append(name)

    def __getattr__(self, attr):
        if attr not in self._extensions:
            raise AttributeError("%s.%s is not loaded, BUG, needs to be registered in init of jumpscale?" % (self.__doc__,attr))

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

    def __str__(self):
        return "loader: %s"%self.__doc__

    __repr__=__str__

locationbases={}
j = Loader("j")
j.events=Loader("j.events")
j.data=Loader("j.data")
j.core=Loader("j.core")
j.core.types=Loader("j.core.types")
j.sal=Loader("j.sal")
j.tools=Loader("j.tools")
j.clients=Loader("j.clients")
j.data.serializer=Loader("j.data.serializer")
j.servers=Loader("j.servers")
j.grid=Loader("j.grid")

from .InstallTools import InstallTools
from .InstallTools import Installer
j.do=InstallTools()
j.do.installer=Installer()

from . import core

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


def findjumpscalelocations(path):
    res=[]
    C=j.do.readFile(path)
    for line in C.split("\n"):
        if line.startswith("class "):
            classname=line.replace("class ","").split(":")[0].split("(",1)[0].strip()
        if line.find("self.__jslocation__")!=-1:
            location=line.split("=",1)[1].replace("\"","").replace("'","").strip()
            res.append((classname,location))
    return res

import json

def findModules():
    result={}
    superroot = j.do.getDirName(__file__)
    for rootfolder in j.do.listDirsInDir(superroot,False,True):
        fullpath0=os.path.join(superroot, rootfolder)
        if fullpath0.find("Event")!=-1:
            import ipdb
            ipdb.set_trace()
            
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

                for (classname,location) in findjumpscalelocations(classfile):
                    print("classfile:%s"%classfile)
                    if classname!=None:
                        loc=".".join(location.split(".")[:-1])
                        print ("location:%s"%(location))
                        item=location.split(".")[-1]
                        if loc not in result:
                            result[loc]=[]
                        result[loc].append((classfile,classname,item))

    j.core.db.set("system.locations",json.dumps(result))

if j.core.db.get("system.locations")==None:
    res=findModules()

locations=json.loads(j.core.db.get("system.locations").decode())
print ("LEN:%s"%len(locations))

for locationbase,llist in locations.items():  #locationbase is e.g. j.sal
    print (locationbase)
    loader=locationbases[locationbase]
    for classfile,classname,item in llist:
        print (" - %s|%s|%s"%(item,classfile,classname))
        loader._register(item,classfile,classname)

# print (locations)



from IPython import embed
print(999)
embed()

j.application.config = j.data.hrd.get(path="%s/hrd/system"%basevar)

j.logger.enabled = j.application.config.getBool("system.logging",default=False)

from core.Dirs import Dirs
j.dirs=Dirs()

from core import errorhandling


print (2)
j.application.init()
print (3)
