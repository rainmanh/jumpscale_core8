from JumpScale import j
from ServiceTemplate import ServiceTemplate
from Service import Service, getProcessDicts
import re
from ActionsBaseMgmt import ActionsBaseMgmt
from ActionsBaseTmpl import ActionsBaseTmpl
from ActionsBaseNode import ActionsBaseNode
# import AYSdb
import json
from AtYourServiceSync import AtYourServiceSync


# class ModelDebugPath(j.core.models.getBaseModel()):
#     name = StringField(default='')
#     host = StringField(default='')


from mongoengine import *

class ModelDebug(j.core.models.getBaseModel()):
    id = StringField(default='')
    host = StringField(default='')
    cache = StringField(default='')
    paths = ListField(StringField())
    cmd_pre = ListField(StringField())
    cmd_post = ListField(StringField())
    restart = ListField(StringField())


    storpath=StringField(default="/tmp/aysfs")
    namespace=StringField(default="dedupe")

    port=IntField(default=22)

    # def save(self):
    #     j.core.models.set(self)


class AtYourServiceDebug():
    """
    example usage:
    ```
    d=j.atyourservice.debug.get("mytest")
    d.setHost("192.168.0.140")
    d.addPath("/opt/jumpscale8/lib")
    d.upload()
    ```

    next time you can do
    ```
    js 'j.atyourservice.debug.upload("mytest")'
    ```

    """

    def __init__(self,name="main"):
        self.model=j.core.models.load(ModelDebug(id=name))
        self._cl=None

    @property
    def cuisine(self):
        if self._cl==None:
            self._cl=j.clients.ssh.get(self.model.host,self.model.port).cuisine
        return self._cl

    def addPath(self,path):
        if path not in self.model.paths:
            self.model.paths.append(path)        
        self.model.save()

    def reset(self):
        j.do.delete(self.model.storpath)

    def setHost(self,host,port=22):
        self.model.host=host
        self.model.port=port
        self.model.save()

    def setCache(self,host):
        self.model.cache=host
        self.model.save()

    def setNamespace(self,namespace):
        self.model.namespace=namespace
        self.model.save()      

    def addCmdPre(self,cmd):
        if cmd not in self.model.cmd_pre:
            self.model.cmd_pre.append(cmd)
        self.model.save()

    def addCmdPost(self,cmd):
        if cmd not in self.model.cmd_post:
            self.model.cmd_post.append(cmd)
        self.model.save()

    def addRestart(self,name):
        if name not in self.model.restart:
            self.model.restart.append(name)        
        self.model.save()


    def installAYSFS(self):
        """
        install AYSFS on host
        """
        self.cuisine.hostfile_set("ayscache",self.model.cache)        
        self.cuisine.run("umount -fl /opt;echo")
        self.cuisine.run("pkill tmux;echo")
        cmd = "cd /usr/local/bin;rm -f aysfs;wget http://stor.jumpscale.org/ays/bin/aysfs"
        self.cuisine.run(cmd,checkok=True)
        cmd = "cd /usr/local/bin;rm -f js8;wget http://stor.jumpscale.org/ays/bin/js8"
        self.cuisine.run(cmd,checkok=True)
        self.cuisine.run("chmod 550 /usr/local/bin/aysfs;chmod 550 /usr/local/bin/js8",checkok=True)
        cmd= "aysfs -auto /opt"
        self.cuisine.tmux_execute(cmd,interactive=True)

    def upload(self,tocache=False,copyconfig=True,bootstrap=False):
        """
        tell the ays filesystem about this directory which will be uploaded to ays filesystem
        """
        self.reset()
        for path in self.model.paths:
            print ("DEDUPE:%s"%path)
            j.tools.sandboxer.dedupe(path, storpath=self.model.storpath, name="0", reset=False, append=True)

        self.cuisine.run("mkdir -p /mnt/ays/cachelocal/dedupe;mkdir -p /etc/ays/local")
        # j.do.copyTree(self.model.storpath+"/files/", "root@%s:/mnt/ays/cachelocal/%s"%(self.model.host,self.model.namespace), \
        #     keepsymlinks=False, deletefirst=False, overwriteFiles=False, rsync=True, ssh=True, sshport=self.model.port, recursive=True)

        if tocache:
            dest="/mnt/ays/cache/dedupe/"
            desthost=self.model.cache
        else:
            dest="/mnt/ays/cachelocal/dedupe/"
            desthost=self.model.host

        cmd ="rsync  -rlptgo --partial --exclude '*.egg-info*/' --exclude '*.dist-info*/' --exclude '*.egg-info*' "
        cmd +="--exclude '*.pyc' --exclude '*.bak' --exclude '*__pycache__*'  -e 'ssh -o StrictHostKeyChecking=no -p 22' "
        cmd +="'/tmp/aysfs/files/' 'root@%s:%s'"%(desthost,dest)
        print (cmd)
        j.do.execute(cmd)

        if not bootstrap:
            j.do.copyTree(self.model.storpath+"/md/0.flist","root@%s:/etc/ays/local/"%(self.model.host),overwriteFiles=True, rsync=True, ssh=True, sshport=self.model.port)
            try:
                pid=self.cuisine.run("pgrep aysfs")
            except:
                self.installAYSFS()
                pid=self.cuisine.run("pgrep aysfs")

            self.cuisine.run("kill -s sigusr1 %s"%pid)
        else:
            self.cuisine.run("pkill aysfs;echo")
            self.cuisine.run("umount -fl /opt;echo")
            self.cuisine.file_unlink("/etc/ays/local/md/0.flist")
            j.do.copyTree(self.model.storpath+"/md/0.flist","root@stor.jumpscale.org:/mnt/Storage/openvcloud/ftp/ays/md/jumpscale.flist",overwriteFiles=True, rsync=True, ssh=True)


        if copyconfig:
            self.cuisine.run("mkdir -p /optvar/hrd/system")
            cmd ="rsync  -rlptgo --partial --exclude '*.egg-info*/' --exclude '*.dist-info*/' --exclude '*.egg-info*' "
            cmd +="--exclude '*.pyc' --exclude '*.bak' --exclude '*__pycache__*'  -e 'ssh -o StrictHostKeyChecking=no -p 22' "
            cmd +="'/optvar/hrd/system/' 'root@%s:/optvar/hrd/system/'"%(self.model.host)
            print (cmd)
            j.do.execute(cmd)            

class AtYourServiceDebugFactory():


    def get(self,name="main"):
        """
        """
        d=AtYourServiceDebug(name=name)
        return d

    def upload(self,name="main"):
        d=self.get(name=name)
        d.upload()  


        # if j.do.checkInstalled("sshfs")==False:
        #     j.do.execute("apt-get install sshfs")
        # cmd="sshfs root@%s:/mnt/ays/cachelocal /mnt/ays/cachelocal"%host
        # j.do.execute(cmd)


