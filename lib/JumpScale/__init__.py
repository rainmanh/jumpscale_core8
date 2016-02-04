
import sys
import os
import socket
import time
import importlib
import importlib.machinery

if sys.platform.startswith("darwin"):

    base="%s/opt/jumpscale8"%os.environ["HOME"]
    basevar="%s/optvar"%os.environ["HOME"]

    # os.environ['JSBASE']='/Users/Shared/jumpscale/'
    if not 'APPDATA' in os.environ:
        os.environ['APPDATA']=basevar
    if not 'TMP' in os.environ:
        os.environ['TMP']=  os.environ['TMPDIR']+"jumpscale/"

    # for p in ["%s/lib"%base,"%s/lib/lib-dynload/"%base,"%s/bin"%base,"%s/lib/plat-x86_64-linux-gnu"%base]:
    #     if p not in sys.path:
    #         sys.path.append(p)
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
# j.data.types=Loader("j.data.types")
j.sal=Loader("j.sal")
j.tools=Loader("j.tools")
j.clients=Loader("j.clients")
j.data.serializer=Loader("j.data.serializer")
j.servers=Loader("j.servers")
j.grid=Loader("j.grid")
j.data.units = Loader('j.data.units')
j.data.models = Loader('j.data.models')

from .InstallTools import InstallTools
from .InstallTools import Installer
j.do=InstallTools()
j.do.installer=Installer()


from . import core

sys.path.append('%s/lib/JumpScale'%j.do.BASE)

import importlib

def redisinit():
    import redis
    j.core.db=redis.Redis(unix_socket_path='/tmp/redis.sock')
    try:
        j.core.db.set("internal.last",0)
    except:
        print ("warning:did not find redis")
        j.core.db=None

import os
redisinit()
if j.core.db==None:

    if j.do.TYPE.startswith("OSX"):
        cmd="redis-server --port 0 --unixsocket /tmp/redis.sock --maxmemory 100000000 --daemonize yes"
        print ("start redis in background")
        os.system(cmd)
    else:
        cmd="echo never > /sys/kernel/mm/transparent_hugepage/enabled"
        os.system(cmd)
        cmd="sysctl vm.overcommit_memory=1"        
        os.system(cmd)
        url="https://stor.jumpscale.org/public/redis-server"
        if 'redis' not in os.listdir(path='%s/bin/'%j.do.BASE):
            j.do.download(url, to='%s/bin/redis'%j.do.BASE, overwrite=False, retry=3)
        import subprocess
        cmd1 = "chmod 550 %sbin/redis > 2&>1"%j.do.BASE
        cmd2 = "%sbin/redis  --port 0 --unixsocket /tmp/redis.sock --maxmemory 100000000 --daemonize yes"%j.do.BASE
        print ("start redis in background")
        os.system(cmd1)
        os.system(cmd2)
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
    if base =="/opt/jumpscale8":
        j.do.writeFile("%s/bin/metadata.db"%j.do.BASE,json.dumps(result))


forcereload=False


if base !="/opt/jumpscale8":
    mdpath="%s/bin/metadata.db"%base
    if j.do.exists(mdpath):
        forcereload=True
        j.do.delete(mdpath)
        #make sure redis is empty
        if j.core.db!=None:
            j.core.db.flushall()
        if base =="/optrw/jumpscale8":
            j.do.installer.writeenv(basedir=base, insystem=False, CODEDIR='/optrw/code')
        print ("force metadata reload")

data=j.core.db.get("system.locations")
if forcereload or data==None:
    if not j.do.exists(path="%s/bin/metadata.db"%j.do.BASE):
        res=findModules()
        data=j.core.db.get("system.locations").decode()
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
