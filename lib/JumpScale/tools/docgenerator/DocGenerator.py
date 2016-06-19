from JumpScale import j

# from mako.template import Template
import pystache

import imp
import sys
import inspect
import copy

def loadmodule(name, path):
    parentname = ".".join(name.split(".")[:-1])
    sys.modules[parentname] = __package__
    mod = imp.load_source(name, path)
    return mod

class DocGenerator:
    """
    """
    def __init__(self):
        self.__jslocation__ = "j.tools.docgenerator"
        self.source=""
        self.gitdir=""
        self.parentgitdir=""
        self.data={}
        mydir=j.sal.fs.getDirName(inspect.getfile(self.process))
        if j.sal.fs.exists(j.sal.fs.joinPaths(mydir,"macros")):
            code=""
            for path in j.sal.fs.listFilesInDir(j.sal.fs.joinPaths(mydir,"macros"), recursive=True, filter="*.py", followSymlinks=True):
                newdata=j.sal.fs.fileGetContents(path)
                code+="%s\n\n%s"%(code,newdata)

            code=code.replace("from JumpScale import j","")
            code="from JumpScale import j\n\n"+code
            codepath=j.sal.fs.joinPaths(j.dirs.tmpDir,"jumpscale8_docgenerator_macros.py")
            j.sal.fs.writeFile(codepath,code)
            self.macros=loadmodule("macros",codepath)
        else:
            raise j.exceptions.Input("Could not find macros in %s"%mydir)

        self._contentPaths={}


    def _loadContentPath(self,path):
        base=j.sal.fs.getBaseName(path).lower()
        base=base[:-3] #remove extension
        if base not in self._contentPaths:
            self._contentPaths[base]=path

    def _loadContentPaths(self):
        """
        walk in right order over all files which we want to potentially use (include)
        and remember their paths
        """

        #go lower then starting point
        for path in j.sal.fs.listFilesInDir(self.source, recursive=True, filter="*.md", followSymlinks=True):
            self._loadContentPath(path)

        #walk up to the tree till .git
        counter=0
        item=self.source
        while not j.sal.fs.exists(j.sal.fs.joinPaths(item,".git")) and counter<10:
            for path2 in j.sal.fs.listFilesInDir(item, recursive=False, filter="*.md", followSymlinks=True):
                self._loadContentPath(path2)
            item=j.sal.fs.getParent(item)
            counter+=1

        if counter==10:
            raise j.exceptions.NotFound("Could not find config.hrd in dir or parent dirs starting from:%s"%source)

        #now go in marked directories
        if 'content.include' in self.config:
            for gititem in self.config['content.include']:
                res=j.do.getGitRepoArgs(gititem)
                gitpath=res[4]
                if not j.sal.fs.exists(gitpath):
                    j.do.pullGitRepo(gititem)
                for path2 in j.sal.fs.listFilesInDir(gitpath, recursive=True, filter="*.md", followSymlinks=True):
                    # print (path2)
                    if path2.find(".git")==-1:
                        self._loadContentPath(path2)

    def process(self,source="",dest=""):
        if source=="":
            source=j.sal.fs.getcwd()

        counter=0
        item=source
        while not j.sal.fs.exists(j.sal.fs.joinPaths(item,"_input")) and counter<10:
            item=j.sal.fs.getParent(item)
            counter+=1

        if counter==10:
            raise j.exceptions.NotFound("Could not find _input in dir or parent dirs starting from:%s"%source)

        self.root=item #is base of doc structure, self.source is starting point
        self.source=j.sal.fs.joinPaths(self.root,"_input")

        self.config=j.data.serializer.yaml.load(j.sal.fs.joinPaths(self.source,"config.yaml"))

        #now look for git directory

        yaml=""

        def checkyaml(yaml,path):
            if j.sal.fs.exists(j.sal.fs.joinPaths(path,"data.yaml")):
                newdata=j.sal.fs.fileGetContents(j.sal.fs.joinPaths(path,"data.yaml"))
                yaml="%s\n%s\n"%(newdata,yaml)
            return yaml


        counter=0
        item=self.source
        while not j.sal.fs.exists(j.sal.fs.joinPaths(item,".git")) and counter<10:
            yaml=checkyaml(yaml,item)
            item=j.sal.fs.getParent(item)
            counter+=1
        yaml=checkyaml(yaml,item)

        if counter==10:
            raise j.exceptions.NotFound("Are we in a .git repo? Could not find .git dir starting search from (parents):%s"%source)

        self.gitdir=item

        self.gitdir_parent=j.sal.fs.getParent(self.gitdir)

        #@todo better errohandling
        self.data=j.data.serializer.yaml.loads(yaml)

        keys=[str(key) for key in self.data.keys()]
        for key in keys:
            if key.find(".")!=-1:
                self.data[key.replace(".","_")]=self.data[key]
                self.data.pop(key)

        self._loadContentPaths()

        #process all files and do includes and other macro's
        for path in j.sal.fs.listFilesInDir(self.source, recursive=True, filter="*.md", followSymlinks=True):
            self.processFile(path)


    def processFile(self,path):
        content=j.sal.fs.fileGetContents(path)
        self.last_content=content
        self.last_path=path
        self.last_dest=j.sal.fs.joinPaths(j.sal.fs.getDirName(path),j.sal.fs.getBaseName(path)[1:])
        # self.last_dest=j.sal.fs.joinPaths(self.root,j.sal.fs.pathRemoveDirPart(path,self.source))
        # j.sal.fs.createDir(j.sal.fs.getDirName(self.last_dest))

        regex="\$\{+\w+\(.*\)\}"
        for match in j.data.regex.yieldRegexMatches(regex, content, flags=0):
            methodcode=match.founditem.strip("${}")
            methodcode=methodcode.replace("(","(self,")

            #find level we are in
            self.last_level=0
            for line in content.split("\n"):
                if line.find(match.founditem)!=-1:
                    #we found position where we are working
                    break
                if line.startswith("#"):
                    self.last_level=len(line.split(" ",1)[0].strip())
            try:
                result=eval("self.macros."+methodcode)
            except Exception as e:
                raise e

            #replace return of function
            content=content.replace(match.founditem,result)


        #lets rewrite our style args to mustache style, so we can use both
        regex="\$\{[a-zA-Z!.]+}"
        for match in j.data.regex.yieldRegexMatches(regex, content, flags=0):
            methodcode=match.founditem.strip("${}").replace(".","_")
            content=content.replace(match.founditem,"{{%s}}"%methodcode)
            

        #process multi line blocks
        state="start"
        block=""
        out=""
        for line in content.split("\n"):
            if state=="blockstart" and (line.startswith("```") or line.startswith("'''")):
                #end of block
                line0=block.split("\n")[0]
                block="\n".join(block.split("\n")[1:])
                if line0.startswith("!!!"):
                    methodcode=line0[3:]
                    methodcode=methodcode.rstrip(", )")#remove end )
                    methodcode=methodcode.replace("(","(self,")
                    methodcode+=",content=block)"
                    methodcode=methodcode.replace(",,",",")
                    try:
                        block=eval("self.macros."+methodcode)
                    except Exception as e:
                        raise e
                out+=block
                block=""
                state="start"
                continue

            if state=="blockstart":
                block+="%s\n"%line
                continue

            if state=="start" and (line.startswith("```") or line.startswith("'''")):
                state="blockstart"
                continue

            out+="%s\n"%line

        content=out
                

        content=pystache.render(content,self.data)

        
        j.sal.fs.writeFile(filename=self.last_dest,contents=content)

        
        # j.data.regex.replace(regexFind, regexFindsubsetToReplace, replaceWith, text)


