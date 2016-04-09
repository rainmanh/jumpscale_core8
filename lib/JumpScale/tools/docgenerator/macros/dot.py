
def dot(self,name,content):
    path=j.sal.fs.getTmpFilePath()
    j.sal.fs.writeFile(filename=path,contents=content)
    dest=j.sal.fs.joinPaths(j.sal.fs.getDirName(self.last_dest),"%s.png"%name)
    j.do.execute("dot '%s' -Tpng > '%s'"%(path,dest))
    j.sal.fs.remove(path)
    return "![%s.png](%s.png)"%(name,name)