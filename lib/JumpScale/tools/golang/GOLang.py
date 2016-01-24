from JumpScale import j
import os

class GOLang:
    def __init__(self):
        self.__jslocation__ = "j.tools.golang"
        self._gopath=""


    def init(self):
        j.tools.bash.addExport("GOPATH",self.gopath)
        j.tools.bash.addPath(self.binpath)
        if j.do.exists("/usr/local/go/bin/go"):
            j.tools.bash.addPath("/usr/local/go/bin/go")

    @property
    def gopath(self):
        if self._gopath=="":
            if 'GOPATH' in os.environ.keys():
                self._gopath=os.environ["GOPATH"]
            else:
                attempt=j.do.joinPaths(os.environ["HOME"],"go")
                if j.do.exists(attempt):
                    os.environ["GOPATH"]=attempt
                else:
                    raise RuntimeError("Could not find gopath")
                self._gopath=os.environ["GOPATH"]
                self.init()
        return self._gopath
    
    @property
    def binpath(self):
        _binpath=j.do.joinPaths(self.gopath,"bin")
        if not j.do.exists(_binpath):
            raise RuntimeError("could not find bindir in gopath")
            
        return _binpath

    def check(self):
        rc,out=j.do.execute("which go",outputStdout=False, outputStderr=False,dieOnNonZeroExitCode=False)
        if rc>0:
            raise RuntimeError("Could not find golang, please install")
        self.gopath

    def build(self,url):
        self.check()
        url=j.data.text.stripItems(url,["git@",".git"])
        url=url.replace(":","/")
        cmd="go get %s"%url
        j.do.execute(cmd)
