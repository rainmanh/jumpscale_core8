from JumpScale import j
import re
from io import StringIO

from tools.cuisine.ActionDecorator import ActionDecorator
class actionrun(ActionDecorator):
    def __init__(self,*args,**kwargs):
        ActionDecorator.__init__(self,*args,**kwargs)
        self.selfobjCode="cuisine=j.tools.cuisine.getFromId('$id');selfobj=cuisine.bash"


class Profile(object):
    env_pattern = re.compile(r'^([^=\n]+)="([^"\n]+)"$', re.MULTILINE)
    include_pattern = re.compile(r'^source (.*)$', re.MULTILINE)

    def __init__(self, content):
        """
        X="value"
        Y="value"
        PATH="p1:p2:p3"

        export X
        export Y
        """
        self._env = {}
        self._path = set()
        self._includes = set()
        for match in Profile.env_pattern.finditer(content):
            self._env[match.group(1)] = match.group(2)
        for match in Profile.include_pattern.finditer(content):
            self._includes.add(match.group(1))

        # load path
        if 'PATH' in self._env:
            path = self._env['PATH']
            self._path = set(path.split(':'))
        else:
            self._path = set()
            self._path.add('${PATH}')

    def addPath(self, path):
        self._path.add(path)

    def addInclude(self, path):
        self._includes.add(path)

    @property
    def path(self):
        return list(self._path)

    def set(self, key, value):
        self._env[key] = value

    def remove(self, key):
        del self._env[key]

    def dump(self):
        parts = ['${PATH}']
        parts.extend(self.path)
        self._env['PATH'] = ':'.join(set(self._path))

        content = StringIO()
        content.write('# environment variables\n')
        for key, value in self._env.items():
            content.write('%s="%s"\n' % (key, value))
            content.write('export %s\n\n' % key)

        content.write('# includes\n')
        for path in self._includes:
            content.write('source %s\n' % path)

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
        self.reset()

    def get(self,cuisine,executor):
        b=Bash()
        b.cuisine=cuisine
        b.executor=executor
        return b

    def reset(self):
        self._environ={}
        self._home=None
        self._profilePath=""
        self._profile=None

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
            for line in self.cuisine.core.run("printenv", profile=True, showout=False,force=True).splitlines():
                if '=' in line:
                    name,val=line.split("=",1)
                    name=name.strip()
                    val=val.strip().strip("'").strip("\"")
                    res[name]=val
            self._environ=res
        merge = self._environ.copy()
        merge.update(self.profile.environ)
        return merge

    @property
    def home(self):
        if not self._home:
            res={}
            for line in self.cuisine.core.run("printenv", profile=False, showout=False,force=True).splitlines():
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
        self._environ[key] = val
        self.profile.set(key, val)
        self.cuisine.core.file_write(self.profilePath, self.profile.dump())
        self.reset()

    @actionrun(action=True)
    def setOurProfile(self):
        mpath=j.sal.fs.joinPaths(self.home,".profile")
        mpath2=j.sal.fs.joinPaths(self.home,".profile_js")
        attempts=[mpath,j.sal.fs.joinPaths(self.home,".bash_profile")]
        path=""
        for attempt in attempts:
            if self.cuisine.core.file_exists(attempt):
                path=attempt

        if path=="":
            path=mpath
            self.cuisine.core.file_write(mpath,". %s\n"%mpath2)
        else:
            out=self.cuisine.core.file_read(path)

            out="\n".join(line for line in out.splitlines() if line.find("profile_js")==-1)

            out+="\n\n. %s\n"%mpath2

            self.cuisine.core.file_write(path,out)
        self.reset()
        return None


    def cmdGetPath(self,cmd,die=True):
        """
        checks cmd Exists and returns the path
        """
        rc,out=self.cuisine.core.run("which %s"%cmd,die=False,showout=False,action=False,profile=True, force=True)
        if rc>0:
            if die:
                raise RuntimeError("Did not find command: %s"%cmd)
            else:
                return False
        return out.split("\n")[-1]


    @property
    def profilePath(self):
        if self._profilePath == "":
            self._profilePath = j.sal.fs.joinPaths(self.home, ".profile_js")
        if not self.cuisine.core.file_exists(self._profilePath):
            self.cuisine.core.file_write(self._profilePath,"")
            self.setOurProfile()
            self._profile = None
        return self._profilePath

    @property
    def profile(self):
        if not self._profile:
            content = ""
            if self.cuisine.core.file_exists(self.profilePath):
                content = self.cuisine.core.file_read(self.profilePath)
            self._profile = Profile(content)
        return self._profile

    @actionrun(action=True)
    def addPath(self, path):
        self.profile.addPath(path)
        self.cuisine.core.file_write(self.profilePath, self.profile.dump(),showout=False)

    @actionrun(action=True)
    def environRemove(self, key, val=None):
        self.profile.remove(key)
        self.cuisine.core.file_write(self.profilePath, self.profile.dump(),showout=False)

    @actionrun(action=True)
    def include(self, path):
        self.profile.addInclude(path)
        self.cuisine.core.file_write(self.profilePath, self.profile.dump(),showout=False)
