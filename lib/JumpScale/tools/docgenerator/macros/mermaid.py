
def mermaid(self,name,content,width=2048):
    path=j.sal.fs.getTmpFilePath()
    j.sal.fs.writeFile(filename=path,contents=content)
    dest=j.sal.fs.joinPaths(j.sal.fs.getDirName(self.last_dest),"%s.png"%name)
    j.do.execute("mermaid -p '%s' -w %s"%(path,width))
    j.sal.fs.remove(path)
    path=path+".png"
    j.sal.fs.copyFile(path,dest)
    return "![%s.png](%s.png)"%(name,name)