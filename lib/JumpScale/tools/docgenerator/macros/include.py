
def include(self,name):
    name=name.lower()
    if name in self._contentPaths:
        newcontent0=j.sal.fs.fileGetContents(self._contentPaths[name])

        newcontent=""


        pre="#"*self.last_level

        for line in newcontent0.split("\n"):
            if line.find("#")!=-1:
                line=pre+line
            newcontent+="%s\n"%line

    else:
        newcontent="COULD NOT INCLUDE:%s (not found)"%name
    return newcontent
    