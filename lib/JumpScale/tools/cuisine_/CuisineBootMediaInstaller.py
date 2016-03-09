
from JumpScale import j
import os
import time

import socket

from ActionDecorator import ActionDecorator
class actionrun(ActionDecorator):
    def __init__(self,*args,**kwargs):
        ActionDecorator.__init__(self,*args,**kwargs)
        self.selfobjCode="cuisine=j.tools.cuisine.getFromId('$id');selfobj=cuisine.bootmediaInstaller"


class CuisineBootMediaInstaller(object):

    def __init__(self,executor,cuisine):
        self.executor=executor
        self.cuisine=cuisine

    @actionrun(action=True)
    def _downloadImage(self,redownload=False):
        base=url.split("/")[-1]
        downloadpath="$tmpDir/%s"%base
        if redownload:
            self.cuisine.file_unlink(downloadpath)

        if not self.cuisine.file_exists(downloadpath):
            self.cuisine.run("cd $tmpDir;wget %s"%url)

        return base

    @actionrun(action=True)
    def formatCardDeployImage(self,url):
        """
        will only work if 1 or more sd cards found of 8 or 16 or 32 GB, be careful will overwrite the card
        executor = a linux machine

        executor=j.tools.executor.getSSHBased(addr="192.168.0.23", port=22,login="root",passwd="rooter",pushkey="ovh_install")
        executor.cuisine.bootmediaInstaller.formatCards()

        """

        j.actions.setRunId("installSD")

        base=self._downloadImage(url)

        def partition(deviceid,size,base):
            cmd="parted -s /dev/%s mklabel msdos mkpar primary fat32 2 100M mkpart primary ext4 100M 100"%deviceid
            cmd+="%"
            self.cuisine.run(cmd)
            self.cuisine.run("umount /mnt/boot",die=False)
            self.cuisine.run("umount /mnt/root",die=False)
            self.cuisine.run("umount /dev/%s1"%deviceid,die=False)
            self.cuisine.run("umount /dev/%s2"%deviceid,die=False)
            self.cuisine.run("mkfs.vfat /dev/%s1"%deviceid)
            self.cuisine.run("mkdir -p /mnt/boot;mount /dev/%s1 /mnt/boot"%deviceid)
            self.cuisine.run("mkfs.ext4 /dev/%s2"%deviceid)
            self.cuisine.run("mkdir -p /mnt/root;mount /dev/%s2 /mnt/root"%deviceid)

            self.cuisine.run("cd $tmpDir;tar vxf %s -C root"%base)

            self.cuisine.run("sync")
            self.cuisine.run("cd /mnt;mv root/boot/* boot")

            self.cuisine.run("echo 'PermitRootLogin=yes'>>'/mnt/root/etc/ssh/sshd_config'")

            self.cuisine.run("umount /mnt/boot",die=False)
            self.cuisine.run("umount /mnt/root",die=False)


        def findDevices():
            devs=[]
            for line in self.cuisine.run("lsblk -b -o TYPE,NAME,SIZE").split("\n"):
                if line.startswith("disk"):
                    while line.find("  ")>0:
                        line=line.replace("  "," ")
                    ttype,dev,size=line.split(" ")
                    size=int(size)
                    if size>30000000000 and size < 32000000000:
                        devs.append((dev,size))
                    if size>15000000000 and size < 17000000000:
                        devs.append((dev,size))
                    if size>7500000000 and size < 8500000000:
                        devs.append((dev,size))
            if len(devs)==0:
                raise RuntimeError("could not find flash disk device, (need to find at least 1 of 8,16 or 32 GB size)"%devs)
            return devs


        devs=findDevices()

        for deviceid,size in devs:
            j.tools.actions.add(partition,actionRecover=None,args=(deviceid,size,base),die=True,stdOutput=False,errorOutput=True,retry=0,executeNow=False,force=False)

        #will make sure they execute in parallel
        j.tools.actions.run()

        return devs


    def arch(self):
        url="http://archlinuxarm.org/os/ArchLinuxARM-rpi-2-latest.tar.gz"
        self.formatCardDeployImage(url)

    def __str__(self):
        return "cuisine.bootmediaInstaller:%s:%s" % (getattr(self.executor, 'addr', 'local'), getattr(self.executor, 'port', ''))


    __repr__=__str__
