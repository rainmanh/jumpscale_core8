from JumpScale import j

import re


class Dep():
    def __init__(self,name,path):
        self.name=name
        self.path=path
        if j.sal.fs.isLink(self.path):
            link=j.sal.fs.readlink(self.path)
            if j.sal.fs.exists(path=link):
                self.path=link
                return
            else:
                base=j.sal.fs.getDirName(self.path)
                potpath=j.sal.fs.joinPaths(base,link)
                if j.sal.fs.exists(potpath):
                    self.path=potpath
                    return
        else:
            if j.sal.fs.exists(self.path):
                return
        raise RuntimeError("could not find lib (dep): '%s'"%self.path)

    def copyTo(self,path):
        dest=j.sal.fs.joinPaths(path,self.name)
        j.sal.fs.createDir(j.sal.fs.getDirName(dest))
        if dest!=self.path:
            j.sal.fs.copyFile(self.path, dest)


    def __str__(self):
        return "%-40s %s"%(self.name,self.path)

    __repr__=__str__

class Sandboxer():
    """
    sandbox any linux app
    """

    def __init__(self):
        self._done=[]
        self.exclude=["libpthread.so","libltdl.so","libm.so","libresolv.so","libz.so","libgcc","librt","libstdc++","libapt","libdbus","libselinux"]

    def _ldd(self,path,result={}):

        if j.sal.fs.getFileExtension(path) in ["py","pyc","cfg","hrd","bak","txt","png","gif","css","js","wiki","spec","sh","jar"]:
            return result

        print(("check:%s"%path))

        cmd="ldd %s"%path
        rc,out=j.sal.process.execute(cmd,dieOnNonZeroExitCode=False)
        if rc>0:
            if out.find("not a dynamic executable")!=-1:
                return result
        for line in out.split("\n"):
            line=line.strip()
            if line=="":
                continue
            if line.find('=>')==-1:
                continue

            name,lpath=line.split("=>")
            name=name.strip().strip("\t")
            name=name.replace("\\t","")
            lpath=lpath.split("(")[0]
            lpath=lpath.strip()
            if lpath=="":
                continue
            if name.find("libc.so")!=0 and name.lower().find("libx")!=0 and name not in self._done \
                and name.find("libdl.so")!=0:
                excl=False
                for toexeclude in self.exclude:
                    if name.lower().find(toexeclude.lower())!=-1:
                        excl=True
                if not excl:
                    print(("found:%s"%name))
                    try:
                        result[name]=Dep(name,lpath)
                        self._done.append(name)
                        result=self._ldd(lpath,result)
                    except Exception as e:
                        print (e)

        return result

    def findLibs(self,path):
        result=self._ldd(path)
        return result

    def copyLibsTo(self,path,dest,recursive=False):
        if j.sal.fs.isDir(path):
            #do all files in dir
            for item in j.sal.fs.listFilesInDir( path, recursive=recursive, followSymlinks=True, listSymlinks=False):
                if j.sal.fs.isExecutable(item) or j.sal.fs.getFileExtension(item)=="so":
                    self.copyLibsTo(item,dest,recursive=recursive)
        else:
            result=self.findLibs(path)
            for name,deb in list(result.items()):
                deb.copyTo(dest)

    def copyTo(self,path,dest,excludeFileRegex=[],excludeDirRegex=[],excludeFiltersExt=["pyc","bak"]):

        print("SANDBOX COPY: %s to %s"%(path,dest))

        excludeFileRegex=[re.compile(r'%s'%item) for item in excludeFileRegex]
        excludeDirRegex=[re.compile(r'%s'%item) for item in excludeDirRegex]
        for extregex in excludeFiltersExt:
            excludeFileRegex.append(re.compile(r'(\.%s)$'%extregex))

        def callbackForMatchDir(path,arg):
            # print ("P:%s"%path)
            for item in excludeDirRegex:
                if(len(re.findall(item, path))>0):
                    return False
            return True

        def callbackForMatchFile(path,arg):
            # print ("F:%s"%path)
            for item in excludeFileRegex:
                if(len(re.findall(item, path))>0):
                    return False
            return True

        def callbackFile(src,args):
            path,dest=args
            subpath=j.sal.fs.pathRemoveDirPart(src,path)
            if subpath.startswith("dist-packages"):
                subpath=subpath.replace("dist-packages/","")
            if subpath.startswith("site-packages"):
                subpath=subpath.replace("site-packages/","")

            dest2=dest+"/"+subpath
            j.do.createDir(j.do.getDirName(dest2))
            # print ("C:%s"%dest2)
            j.do.copyFile(src,dest2)


        j.system.fswalker.walkFunctional(path, callbackFunctionFile=callbackFile, callbackFunctionDir=None, arg=(path,dest), \
            callbackForMatchDir=callbackForMatchDir, callbackForMatchFile=callbackForMatchFile)


    def dedupe(self, path, storpath, name, excludeFiltersExt=["pyc","bak"],append=False,reset=False,removePrefix=""):
        def _calculatePaths(src, removePrefix):
            if j.sal.fs.isLink(src):
                srcReal = j.sal.fs.readlink(src)
                if not j.sal.fs.isAbsolute(srcReal):
                    srcReal = j.sal.fs.joinPaths(j.sal.fs.getParent(src), srcReal)
            else:
                srcReal = src

            md5 = j.tools.hash.md5(srcReal)
            dest2 = "%s/%s/%s/%s" % (storpath2, md5[0], md5[1], md5)
            j.do.copyFile(srcReal, dest2)

            stat = j.sal.fs.statPath(srcReal)

            if removePrefix != "":
                if src.startswith(removePrefix):
                    src = src[len(removePrefix):]
                    if src[0] != "/":
                        src = "/" + src

            out = "%s|%s|%s\n" % (src, md5, stat.st_size)
            return out

        if reset:
            j.do.delete(storpath)
        storpath2 = j.sal.fs.joinPaths(storpath, "files")
        j.sal.fs.createDir(storpath2)
        j.sal.fs.createDir(j.sal.fs.joinPaths(storpath, "md"))
        for i1 in "1234567890abcdef":
            for i2 in "1234567890abcdef":
                j.do.createDir("%s/%s/%s" % (storpath2, i1, i2))

        print("DEDUPE: %s to %s" % (path, storpath))

        plistfile = j.sal.fs.joinPaths(storpath, "md", "%s.flist" % name)

        if append and j.sal.fs.exists(path=plistfile):
            out = j.sal.fs.fileGetContents(plistfile)
        else:
            j.do.delete(plistfile)
            out = ""

        # excludeFileRegex=[]
        # for extregex in excludeFiltersExt:
        #     excludeFileRegex.append(re.compile(ur'(\.%s)$'%extregex))

        if not j.sal.fs.isDir(path):
            out += _calculatePaths(path, removePrefix)
        else:
            for src in j.sal.fs.listFilesInDir(path, recursive=True, exclude=["*.pyc", "*.git*"], followSymlinks=True, listSymlinks=True):
                out += _calculatePaths(src, removePrefix)

        out = j.tools.text.sort(out)
        j.sal.fs.writeFile(plistfile, out)
