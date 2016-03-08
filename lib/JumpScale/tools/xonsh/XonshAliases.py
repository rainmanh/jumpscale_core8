
from JumpScale import j


def xonsh_go(args, stdin=None):
    lookfor=args[0]
    #walk over github dirs, try to find lookfor
    res=[]
    for subdir in j.sal.fs.listDirsInDir(j.dirs.codeDir+"/github/",False,True):
        curpath="%s/github/%s/"%(j.dirs.codeDir,subdir)
        for subdir2 in j.sal.fs.listDirsInDir(curpath,False,True):
            curpath2=j.sal.fs.joinPaths(curpath,subdir2)
            print (curpath2)
            if subdir2.find(lookfor)!=-1:
                res.append(curpath2)
    path=j.tools.console.askChoice(res,"Select directory to go to.")
    
    if len(args)>1:
        #means look for subdir in found current path
        res=j.sal.fs.listDirsInDir(path,True)
        res=[item for item in res if j.sal.fs.getBaseName(item)[0]!="."]
        res=[item for item in res if j.sal.fs.getBaseName(item).find(args[1])!=-1]        
        path=j.tools.console.askChoice(res,"Select sub directory to go to.")

    j.sal.fs.changeDir(path)

def xonsh_edit(args, stdin=None):
    if len(args)==0:
        cmd="/Applications/Sublime\ Text.app/Contents/SharedSupport/bin/subl -a ."
        j.do.executeInteractive(cmd)
        return
    else:
        items=[item for item in j.sal.fs.listFilesInDir(j.sal.fs.getcwd(),exclude=["*.pyc"]) if j.sal.fs.getBaseName(item).find(args[0])!=-1] 
        if len(items)==0:
            print("cannot find file with filter '%s' in %s"%(args[0],j.sal.fs.getcwd()))
            sys.exit()
        path=j.tools.console.askChoice(items,"Select file to edit.")
    
    if j.sal.fs.exists("/Applications/Sublime Text.app"):
        #osx
        cmd="open -a Sublime\ Text %s"%path

    elif j.sal.fs.exists("/usr/bin/subl"):
        raise RuntimeError("implement")        
    else:
        raise RuntimeError("Did not find editor")

    j.do.executeInteractive(cmd)
