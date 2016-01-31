from JumpScale import j
import os

class Bash:
    def __init__(self):
        self.__jslocation__ = "j.tools.bash"
        self._profilePath=""
        self._profile=""


    @property
    def profilePath(self):
        if self._profilePath=="":
            attempts=[j.do.joinPaths(os.environ["HOME"],".bash_profile")]
            for attempt in attempts:
                if j.do.exists(attempt):
                    self._profilePath=attempt
                    return attempt
            else:
                raise RuntimeError("Could not find bash profile")
        return self._profilePath
    
    @property
    def profile(self):
        if self._profile=="":
            self._profile=j.do.readFile(self.profilePath)
        return self._profile

    @profile.setter
    def profile(self,val):
        if val!=self.profile:
            self._profile=val
            j.sal.fs.writeFile(filename=self.profilePath,contents=val)

    def addPath(self,path):
        self.addExport("PATH","%s:${PATH}"% path)

    def remove(self,key,val):
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

    def addExport(self,key,val,isString=True):
        """
        @param multiItems = True, will then look for multiple x=a,y=b, ... on 1 line
        """

        self.remove(key,val)
        out=self.profile

        if isString:
            out+="%s=\"%s\"\n"%(key,val)
        else:
            out+="%s=%s\n"%(key,val)

        out+="export %s\n"%key
        out=out.replace("\n\n\n","\n\n")
        # print(out)
        self.profile=out

