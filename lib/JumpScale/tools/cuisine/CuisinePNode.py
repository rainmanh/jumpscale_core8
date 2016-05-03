
from JumpScale import j


class CuisinePNode():

    def __init__(self, executor, cuisine):
        self.executor = executor
        self.cuisine = cuisine

    @property
    def hwplatform(self):
        """
        example: hwplatform = rpi_2b, orangepi_plus,amd64
        """
        #@todo (*1*)
        


    def erase(self,keepRoot=True):
        """
        if keepRoot==True:
            find boot/root partitions and leave them untouched (check if mirror, leave too)
        clean/remove all (other) disks/partitions
        """
        if self.hwplatform!="amd64":
            raise j.exceptions.Input("only amd64 hw platform supported")
        #@todo (*1*)

    def formatStorage(self,keepRoot=True,mountpoint="/storage"):
        """
        use btrfs to format/mount the disks
        use metadata & data in raid1 (if at least 2 disk)
        make sure they are in fstab so survices reboot
        """
        if self.hwplatform!="amd64":
            raise j.exceptions.Input("only amd64 hw platform supported")
        #@todo (*1*)



    def buildG8OSImage(self):
        """
        
        """
        #@todo cuisine enable https://github.com/g8os/builder

    def buildArchImage(self):
        """
        
        """


    def installArch(self,rootsize=5):
        """
        install arch on $rootsize GB root partition
        """
        if self.hwplatform!="amd64":
            raise j.exceptions.Input("only amd64 hw platform supported")
        #manual partitioning
        #get tgz from url="https://stor.jumpscale.org/public/ubuntu....tgz"


    def installG8OS(self,rootsize=5):
        """
        install g8os on $rootsize GB root partition
        """
        if self.hwplatform!="amd64":
            raise j.exceptions.Input("only amd64 hw platform supported")
        #manual partitioning
        #get tgz from url="https://stor.jumpscale.org/public/ubuntu....tgz"

