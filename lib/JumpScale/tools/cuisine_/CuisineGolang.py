
from JumpScale import j
# import os

# import socket

from ActionDecorator import ActionDecorator
class actionrun(ActionDecorator):
    def __init__(self,*args,**kwargs):
        ActionDecorator.__init__(self,*args,**kwargs)
        self.selfobjCode="cuisine=j.tools.cuisine.getFromId('$id');selfobj=cuisine.golang"



class CuisineGolang():

    def __init__(self,executor,cuisine):
        self.executor=executor
        self.cuisine=cuisine

    @actionrun(action=True)
    def install(self):
        self.cuisine.installer.base()
        optdir=self.cuisine.dir_paths["optDir"]
        rc, out = self.cuisine.run("which go", die=False,showout=False,action=True)
        if rc > 0:
            if self.cuisine.isMac or self.cuisine.isArch:
                self.cuisine.package.install("go")
            elif "ubuntu" in self.cuisine.platformtype.platformtypes:
                # self.cuisine.run("apt-get install golang -y --force-yes")
                downl="https://storage.googleapis.com/golang/go1.5.3.linux-amd64.tar.gz"
                self.cuisine.file_download(downl,"/usr/local",overwrite=False,retry=3,timeout=0,expand=True)
            else:
                raise RuntimeError("platform not supported")

        self.cuisine.bash.environSet("GOPATH", '%s/go'%optdir)

        self.cuisine.bash.addPath('/usr/local/go/bin')
        self.cuisine.bash.addPath('%s/go/bin'%optdir)

        self.cuisine.createDir("%s/go/src"%optdir)
        self.cuisine.createDir("%s/go/pkg"%optdir)
        self.cuisine.createDir("%s/go/bin"%optdir)

        print ('GOPATH:', self.cuisine.bash.environ["GOPATH"])

        self.get("github.com/tools/godep")
        # self.get("github.com/rcrowley/go-metrics")


    @property
    def GOPATH(self):
        return self.cuisine.dir_paths["goDir"]
        # if self._gopath==None:
        #     # if not "GOPATH" in self.bash.environ:
        #     #     self.cuisine.installerdevelop.golang()
        #     # self._gopath=   self.bash.environ["GOPATH"]

        # return self._gopath


    @actionrun(action=True)
    def get(self,url):
        """
        e.g. url=github.com/tools/godep
        """
        self.cuisine.run('go get -x -u %s'%url,profile=True)
