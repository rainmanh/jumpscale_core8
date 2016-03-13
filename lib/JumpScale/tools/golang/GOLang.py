from JumpScale import j
import os

class GOLang:
    def __init__(self):
        self.__jslocation__ = "j.tools.golang"
        self._gopath=""


    def init(self):
        j.tools.bash.addExport("GOPATH",self.gopath)
        j.tools.bash.addPath(self.binpath)
        if j.sal.fs.exists("/usr/local/go/bin/go"):
            j.tools.bash.addPath("/usr/local/go/bin/go")

    @property
    def gopath(self):
        if self._gopath=="":
            if 'GOPATH' in os.environ.keys():
                self._gopath=os.environ["GOPATH"]
            else:
                attempt=j.sal.fs.joinPaths(os.environ["HOME"],"go")
                if j.sal.fs.exists(attempt):
                    os.environ["GOPATH"]=attempt
                else:
                    raise RuntimeError("Could not find gopath")
                self._gopath=os.environ["GOPATH"]
                self.init()
        return self._gopath
    
    @property
    def binpath(self):
        _binpath=j.sal.fs.joinPaths(self.gopath,"bin")
        if not j.sal.fs.exists(_binpath):
            raise RuntimeError("could not find bindir in gopath")
            
        return _binpath

    def check(self):
        rc,out=j.sal.process.execute("which go",outputToStdout=False, outputStderr=False,die=False)
        if rc>0:
            raise RuntimeError("Could not find golang, please install")
        self.gopath

    def build(self, url):
        self.check()
        dest = j.data.text.stripItems(url, ["git@", ".git"])
        dest = dest.replace(":", "/")
        dest = j.do.pullGitRepo(url, dest=j.sal.fs.joinPaths(os.environ['GOPATH'], 'src', dest))

        executor = j.tools.executor.getLocal()
        executor.execute('cd %s && godep restore' % dest)
        executor.execute('cd %s && go install' % dest)
        return dest
