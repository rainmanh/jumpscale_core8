
import sys
import os
import socket
import time
import importlib
import importlib.machinery

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
else:
    if "JSBASE" not in os.environ:
        os.environ["JSBASE"]="/opt/jumpscale8"
        # raise RuntimeError("Cannot load jumpscale, please specify JSBASE as env variable.")
    base=os.environ["JSBASE"]
    basevar="/optvar"

import os.path


if not os.path.isfile("%s/lib/lsb_release.py"%base):
    sys.path.insert(0,"%s/lib"%base)
    sys.path.insert(0,"%s/bin"%base)
    sys.path.insert(0,"%s/lib/JumpScale"%base)
    sys.path.insert(0,"%s/lib/lib-dynload"%base)

else:
    # print ("sandbox")
    sys.path=[]
    sys.path.append("%s/lib"%base)
    sys.path.append("%s/bin"%base)
    sys.path.append("%s/lib/JumpScale"%base)
    sys.path.append("%s/lib/lib-dynload"%base)


class Loader(object):
    def __init__(self,name):
        self.__doc__=name
        locationbases[name]=self
        self._extensions = {}
        self.__members__ = []

    def _register(self, name,classfile,classname):
        # print ("%s   register:%s"%(self.__doc__,name))
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

sys.path.append('%s/lib/JumpScale'%j.do.BASE)

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
    j.do.download(url, to='%s/bin/redis'%j.do.BASE, overwrite=False, retry=3)
    import subprocess
    cmd="chmod 550 %s/bin/redis > 2&>1;%s/bin/redis --unixsocket /tmp/redis.sock --maxmemory 100000000 --daemonize yes"%(j.do.BASE,j.do.BASE)
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
    if os.path.isdir(j.do.BASE):
        superroot="%s/lib/JumpScale"%j.do.BASE
    else:
        if j.core.db.get("system.superroot")==None:  
            superroot = j.do.getDirName(__file__)
            j.core.db.set("system.superroot",superroot)
        superroot=j.core.db.get("system.superroot").decode()

    print ("FINDMODULES in %s"%superroot)
    for rootfolder in j.do.listDirsInDir(superroot,False,True):
        fullpath0=os.path.join(superroot, rootfolder)            
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
                    # print("classfile:%s"%classfile)
                    if classname!=None:
                        loc=".".join(location.split(".")[:-1])
                        print ("location:%s"%(location))
                        item=location.split(".")[-1]
                        if loc not in result:
                            result[loc]=[]
                        result[loc].append((classfile,classname,item))

    j.core.db.set("system.locations",json.dumps(result))
    j.do.writeFile("%s/bin/metadata.db"%j.do.BASE,json.dumps(result))

forcereload=False
if base !="/opt/jumpscale8":
    mdpath="%s/bin/metadata.md"%base
    if j.do.exists(mdpath):
        forcereload=True
    j.do.delete(mdpath)
    

data=j.core.db.get("system.locations")
if forcereload or data==None:
    if not j.do.exists(path="%s/bin/metadata.db"%j.do.BASE):        
        res=findModules()
        data=j.core.db.get("system.locations")
    else:
        data=j.do.readFile("%s/bin/metadata.db"%j.do.BASE)
        # print ("data from readfile")
else:
    data=data.decode()
    
locations=json.loads(data)
# print ("LEN:%s"%len(locations))

for locationbase,llist in locations.items():  #locationbase is e.g. j.sal
    # print (locationbase)
    loader=locationbases[locationbase]
    for classfile,classname,item in llist:
        # print (" - %s|%s|%s"%(item,classfile,classname))
        loader._register(item,classfile,classname)

if not j.do.exists("%s/hrd/system/system.hrd"%basevar):
    j.do.installer.writeenv(die=False)


data=j.core.db.get("system.dirs.%s"%j.do.BASE)
if data==None:
    j.application._config = j.data.hrd.get(path="%s/hrd/system"%basevar)

j.application.init()


