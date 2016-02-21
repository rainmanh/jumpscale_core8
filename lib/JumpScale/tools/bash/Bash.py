from JumpScale import j
import re
from io import StringIO

from tools.cuisine_.ActionDecorator import ActionDecorator
class actionrun(ActionDecorator):
    def __init__(self,*args,**kwargs):
        ActionDecorator.__init__(self,*args,**kwargs)
        self.selfobjCode="cuisine=j.tools.cuisine.getFromId('$id');selfobj=cuisine.bash"


class Profile(object):
    pattern = re.compile(r'^([^=\n]+)="([^"\n]+)"$', re.MULTILINE)

    def __init__(self, content):
        """
        X="value"
        Y="value"
        PATH="p1:p2:p3"

        export X
        export Y
        """
        self._env = {}
        self._path = []
        for match in Profile.pattern.finditer(content):
            self._env[match.group(1)] = match.group(2)

        #load path
        if 'PATH' in self._env:
            path = self._env['PATH']
            self._path = path.split(':')
        else:
            self._path = ['${PATH}']


    def addPath(self, path):
        self._path.append(path)

    @property
    def path(self):
        return self._path

    def set(self, key, value):
        self._env[key] = value

    def remove(self, key):
        del self._env[key]

    def dump(self):
        parts = ['${PATH}']
        parts.extend(self._path)
        self._env['PATH'] = ':'.join(set(self._path))

        content = StringIO()
        for key, value in self._env.items():
            content.write('%s="%s"\n' % (key, value))
            content.write('export %s\n\n' % key)

        return content.getvalue()

    @property
    def environ(self):
        return self._env


class Bash:
    def __init__(self):
        self.__jslocation__ = "j.tools.bash"
        self._profilePath=""
        self._profile=None
        self.cuisine=j.tools.cuisine.get()
        self.executor=self.cuisine.executor
        self._reset()

    def get(self,cuisine,executor):
        b=Bash()
        b.cuisine=cuisine
        b.executor=executor
        return b

    def _reset(self):
        self._environ={}
        self._home=None

    def replaceEnvironInText(self,text):
        """
        will look for $ENVIRONNAME 's and replace them in text
        """
        for key,val in self.environ.items():
            text=text.replace("$%s"%key,val)
        return text

    @property
    def environ(self):
        if self._environ=={}:
            res={}
            for line in self.cuisine.run("printenv", profile=True, showout=False).splitlines():
                if '=' in line:
                    name,val=line.split("=",1)
                    name=name.strip()
                    val=val.strip().strip("'").strip("\"")
                    res[name]=val
            self._environ=res
        return self._environ

    @property
    def home(self):
        if not self._home:
            res={}
            for line in self.cuisine.run("printenv", profile=False, showout=False).splitlines():
                if '=' in line:
                    name, val=line.split("=", 1)
                    name=name.strip()
                    val=val.strip().strip("'").strip("\"")
                    res[name]=val
            self._home=res["HOME"]
        return self._home

    def environGet(self,name,default=None):
        """
        Get environ
        """
        return self.profile.environ.get(name, default)


    def environSet(self,key,val,temp=False):
        """
        Set environ
        """
        self.profile.set(key, val)
        self.cuisine.file_write(self.profilePath, self.profile.dump())

    # @actionrun(action=True)
    def setOurProfile(self):
        mpath=j.do.joinPaths(self.home,".profile")
        mpath2=j.do.joinPaths(self.home,".profile_js")
        attempts=[mpath,j.do.joinPaths(self.home,".bash_profile")]
        path=""
        for attempt in attempts:
            if self.cuisine.file_exists(attempt):
                path=attempt

        if path=="":
            path=mpath
            self.cuisine.file_write(mpath,". %s\n"%mpath2)
        else:
            out=self.cuisine.file_read(path)

            out="\n".join(line for line in out.splitlines() if line.find("profile_js")==-1)

            out+="\n\n. %s\n"%mpath2

            self.cuisine.file_write(path,out)

        return None


    def cmdGetPath(self,cmd,die=True):
        """
        checks cmd Exists and returns the path
        """
        rc,out=self.cuisine.run("which %s"%cmd,die=False,showout=False,action=False,profile=True)
        if rc>0:
            if die:
                raise RuntimeError("Did not find command: %s"%cmd)
            else:
                return False
        return out.split("\n")[-1]


    @property
    def profilePath(self):
        if self._profilePath=="":
            self._profilePath=j.do.joinPaths(self.home,".profile_js")
            if not self.cuisine.file_exists(self._profilePath):
                self.cuisine.file_write(self._profilePath,"")
                self.setOurProfile()
                self._profile=""
        return self._profilePath

    @property
    def profile(self):
        if not self._profile:
            content = self.cuisine.file_read(self.profilePath)
            self._profile = Profile(content)
        return self._profile

    @actionrun()
    def addPath(self, path):
        self.profile.addPath(path)
        self.cuisine.file_write(self.profilePath, self.profile.dump())

    def environRemove(self, key, val=None):
        self.profile.remove(key)
        self.cuisine.file_write(self.profilePath, self.profile.dump())

    def include(self, path):
        content = self.cuisine.file_read(self.profilePath)
        include = 'source %s' % path
        if content.find(include) == -1:
            self.cuisine.file_append(self.profilePath, 'source %s' % path)
