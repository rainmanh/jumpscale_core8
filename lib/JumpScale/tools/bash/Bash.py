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
        if name not in self.environ and default!=None:
            self.environSet(name,default)

        return self.environ[name]
            

    def environSet(self,key,val,temp=False):
        """
        """
        isString=True
        if temp==False:
            if key not in self.environ or self.environ[key]!=val:
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

        #doesn't remember it anyhow, so no need
        # self.cuisine.run("export %s=\"%s\""%(key,val),profile=False,showout=False)

        self._environ[key]=val

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
        if self._profile=="":
            self._profile=self.cuisine.file_read(self.profilePath)
        return self._profile

    @profile.setter
    def profile(self,val):
        if val!=self.profile:
            self._profile=val
            self.cuisine.file_write(self.profilePath,val)


    @actionrun()
    def addPath(self,path):
        self.environSet("PATH","%s:${PATH}"% path)

    def environRemove(self,key,val):
        #@todo needs to be properly checked
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
                    # if line.find("${%s}"%key)==-1:
                    #     continue
                    # else:                        
                    #check if line is empty after removing all things we don't need, if so we can continue
                    line3=j.data.text.stripItems(line,items=["%s"%key,"\""," ","'",":","${%s}"%key,"=",","])
                    if line3=="":
                        continue
            line2=line.replace("  "," ")
            if line2.startswith("export %s"%key):
                continue
            out+="%s\n"%line2

        self.profile=out

