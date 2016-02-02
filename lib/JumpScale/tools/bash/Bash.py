from JumpScale import j

from tools.cuisine_.ActionDecorator import ActionDecorator
class actionrun(ActionDecorator):
    def __init__(self,*args,**kwargs):
        ActionDecorator.__init__(self,*args,**kwargs)
        self.selfobjCode="cuisine=j.tools.cuisine.getFromId('$id');selfobj=cuisine.bash"


class Bash:
    def __init__(self):
        self.__jslocation__ = "j.tools.bash"
        self._profilePath=""
        self._profile=""
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

    @property
    def environ(self):
        if self._environ=={}:
            res={}
            for line in self.cuisine.run("export",profile=True).splitlines():
                if line.startswith("declare -x "):
                    line=line[11:]
                    name,val=line.split("=",1)
                    name=name.strip()
                    val=val.strip().strip("'").strip("\"")
                    res[name]=val
            self._environ=res
        return self._environ

    @property
    def home(self):
        if self._home==None:
            res={}
            for line in self.cuisine.run("export",profile=False).splitlines():
                if line.startswith("declare -x "):
                    line=line[11:]
                    name,val=line.split("=",1)
                    name=name.strip()
                    val=val.strip().strip("'").strip("\"")
                    res[name]=val
            self._home=res["HOME"]        
        return self._home    

    def environGet(self,name,default=None):  
        if name not in self.environ and default!=None:
            self.environSet(name,default)

        return self.environ[name]
            

    def environSet(self,key,val,temp=False):
        """
        """
        isString=True
        if temp==False:
            if key not in self.environ:
                self.environRemove(key,val)
                out=self.profile

                if isString:
                    out+="%s=\"%s\"\n"%(key,val)
                else:
                    out+="%s=%s\n"%(key,val)

                out+="export %s\n"%key
                out=out.replace("\n\n\n","\n\n")
                # print(out)
                self.profile=out

        self.cuisine.run("export %s=\"%s\""%(key,val),profile=False)

        self._environ[key]=val

    def profilePathExists(self):
        mpath=j.do.joinPaths(self.home,".profile")
        attempts=[mpath,j.do.joinPaths(self.home,".bash_profile")]
        for attempt in attempts:
            if self.cuisine.file_exists(attempt):
                self._profilePath=attempt
                return attempt
        return None

    @property
    def profilePath(self):
        if self._profilePath=="":
            self._profilePath=self.profilePathExists()
            if self._profilePath==None:
                self.cuisine.file_write(mpath,"")
                self._profilePath=mpath
        return self._profilePath
    
    @property
    def profile(self):
        if self._profile=="":
            self._profile=self.cuisine.file_read(self.profilePath)
        return self._profile

    @profile.setter
    def profile(self,val):
        if val!=self.profile:
            self._profile=val
            self.cuisine.file_write(self.profilePath,val)

    def addPath(self,path):
        self.environSet("PATH","%s:${PATH}"% path)

    def environRemove(self,key,val):
        content=self.profile
        out=""
        for line in content.split("\n"):
            if line.find("=")!=-1:
                name,args=line.split("=")
                name=name.strip()
                if name==key:
                    line=line.replace(val+",","")
                    line=line.replace(val+" ,","")
                    line=line.replace(val+":","")
                    line=line.replace(val+" :","")
                    line=line.replace(val,"")
                    if line.find("${%s}"%key)==-1:
                        continue
                    else:                        
                        line3=j.data.text.stripItems(line,items=["%s"%key,"\""," ","'",":","${%s}"%key,"=",","])
                        if line3=="":
                            continue
            line2=line.replace("  "," ")
            if line2.startswith("export %s"%key):
                continue
            out+="%s\n"%line
        self.profile=out



