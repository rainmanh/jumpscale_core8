
def mermaid(self,name,content,width=2048):
    path=j.sal.fs.getTmpFilePath()
    content2=""
    for item in content.split("\n"):
        itemstrip=item.strip()
        if itemstrip!="" and itemstrip[0]=="%":
            continue
        content2+="%s\n"%item
    j.sal.fs.writeFile(filename=path,contents=content2)
    dest=j.sal.fs.joinPaths(j.sal.fs.getDirName(self.last_dest),"%s.png"%name)
    cmd="mermaid -p '%s' -w %s"%(path,width)
    res=j.do.execute(cmd)    
    j.sal.fs.remove(path)
    path=path+".png"
    j.sal.fs.moveFile(j.sal.fs.getBaseName(path),dest)
    return "![%s.png](%s.png)"%(name,name)
