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
    process all markdown files in a git repo, write a summary.md file
    optionally call pdf gitbook generator to produce a pdf
    """

    def __init__(self):
        self.__jslocation__ = "j.tools.docgenerator"

    def get(self, source="", pdfpath="", macrosPath=""):
        """
        will look for config.yaml in $source/config.yaml

        @param source is the location where the markdown docs are which need to be processed
            if not specified then will look for root of git repo and add docs
            source = $gitrepoRootDir/docs

        @param pdfpath if specified will generate a pdf using the gitbook tools (needs to be installed)
            if pdfpath=="auto" then put $reponame.pdf in $dest dir

        @param macropath if "" then will look for subdir macro from source dir

        """
        return DocGeneratorItem(source, pdfpath, macrosPath=macrosPath)


class DocGeneratorItem:
    """
    """

    def __init__(self, source="", pdfpath="", macrosPath=""):
        if source == "":
            source = j.sal.fs.getcwd()

            source2 = j.sal.fs.joinPaths(source, "docs")
            if j.sal.fs.getBaseName(j.sal.fs.getcwd()) in ["docs", "doc"]:
                source = j.sal.fs.getcwd()
            elif j.sal.fs.exists(path=source2):
                source = source2
            else:
                counter = 0
                item = source
                while not j.sal.fs.exists(j.sal.fs.joinPaths(item, ".git")) and counter < 10:
                    item = j.sal.fs.getParent(item)
                    counter += 1
                if counter == 10:
                    raise j.exceptions.NotFound("Could not find .git in dir or parent dirs starting from:%s" % source)

                source = j.sal.fs.joinPaths(item, "docs")
                if not j.sal.fs.exists(path=source):
                    source = j.sal.fs.joinPaths(item, "doc")

        if not j.sal.fs.exists(path=source):
            raise j.exceptions.NotFound("Cannot find source path:'%s'" % source)

        self.source = source

        configpath = j.sal.fs.joinPaths(self.source, "config.yaml")
        if j.sal.fs.exists(path=configpath):
            self.config = j.data.serializer.yaml.load(configpath)
        else:
            self.config = {}

        self._contentPaths = {}
        self._macroCodepath = j.sal.fs.joinPaths(j.dirs.tmpDir, "jumpscale8_docgenerator_macros.py")
        j.sal.fs.remove(self._macroCodepath)
        self.loadMacros("self")

        if macrosPath == "":
            macrosPath = j.sal.fs.joinPaths(self.source, "macros")

        if j.sal.fs.exists(path=macrosPath):
            self.loadMacros(macrosPath)

        if pdfpath == "auto":
            basename = j.sal.fs.getBaseName(self.source)
            if basename == "doc":
                basename = j.sal.fs.getBaseName(j.sal.fs.getParent(self.source))
            pdfpath = j.sal.fs.joinPaths(self.source, "%s.pdf" % basename)

        self.pdfpath = pdfpath

        self.loadIncludes(self.source)

        # now go in configured git directories
        if 'content.include' in self.config:
            for gititem in self.config['content.include']:
                res = j.do.getGitRepoArgs(gititem)
                gitpath = res[4]
                if not j.sal.fs.exists(gitpath):
                    j.do.pullGitRepo(gititem)
                self.load(gitpath)

        self.data = {}

    def loadMacros(self, path=""):
        """
        @param path if '' then will try to find macro dir in current dir
        """
        if path == "self":
            mydir = j.sal.fs.getDirName(inspect.getfile(self.process))
            macrodir = j.sal.fs.joinPaths(mydir, "macros")
            return self.loadMacros(macrodir)
        elif path == "":
            mydir = j.sal.fs.getDirName(inspect.getfile(self.process))
            return self.loadMacros(mydir)

        if not j.sal.fs.exists(path=path):
            raise j.exceptions.Input("Cannot find path:'%s' for macro's, does it exist?")

        if j.sal.fs.exists(path=self._macroCodepath):
            code = j.sal.fs.readFile(self._macroCodepath)
        else:
            code = ""

        for path0 in j.sal.fs.listFilesInDir(path, recursive=True, filter="*.py", followSymlinks=True):
            newdata = j.sal.fs.fileGetContents(path0)
            code += "%s\n\n%s" % (code, newdata)

        code = code.replace("from JumpScale import j", "")
        code = "from JumpScale import j\n\n" + code

        j.sal.fs.writeFile(self._macroCodepath, code)
        self.macros = loadmodule("macros", self._macroCodepath)

    def loadIncludes(self, path=""):
        """
        walk in right order over all files which we want to potentially use (include)
        and remember their paths
        if path=='' then will look for .git parent and start from there

        if duplicate only the first found will be used

        """

        if path == "":
            # walk up to the tree till .git
            counter = 0
            item = self.source
            while not j.sal.fs.exists(j.sal.fs.joinPaths(item, ".git")) and counter < 10:
                for path2 in j.sal.fs.listFilesInDir(item, recursive=False, filter="*.md", followSymlinks=True):
                    self._loadContentPath(path2)
                item = j.sal.fs.getParent(item)
                counter += 1

            if counter == 10:
                raise j.exceptions.NotFound("Could not find config.hrd in dir or parent dirs starting from:%s" % source)

            path = item

        if not j.sal.fs.exists(path=path):
            raise j.exceptions.NotFound("Cannot find source path in load:'%s'" % path)

        def callbackForMatchDir(path, arg):
            base = j.sal.fs.getBaseName(path)
            if base.startswith("."):
                return False
            return True

        def callbackForMatchFile(path, arg):
            base = j.sal.fs.getBaseName(path)
            if not j.sal.fs.getFileExtension(path) == "md":
                return False
            if base.startswith("_"):
                return False
            base = j.sal.fs.getBaseName(path).lower()
            base = base[:-3]  # remove extension
            if base in ["summary"]:
                return False
            return True

        def callbackFunctionFile(path, arg):
            base = j.sal.fs.getBaseName(path).lower()
            base = base[:-3]  # remove extension
            if base not in self._contentPaths:
                self._contentPaths[base] = path

        j.sal.fs.walker.walkFunctional(self.source, callbackFunctionFile=callbackFunctionFile, callbackFunctionDir=None, arg="",
                                       callbackForMatchDir=callbackForMatchDir, callbackForMatchFile=callbackForMatchFile)

    def process(self):

        def callbackForMatchDir(path, arg):
            base = j.sal.fs.getBaseName(path)
            if base.startswith("."):
                return False
            return True

        def callbackForMatchFile(path, arg):
            base = j.sal.fs.getBaseName(path)
            return j.sal.fs.getFileExtension(path) == "md" and base.startswith("_")

        def callbackFunctionDir(path, arg):
            yamlfile = j.sal.fs.joinPaths(path, "data.yaml")
            if j.sal.fs.exists(yamlfile):
                newdata = j.data.serializer.yaml.load(yamlfile)

                # dont know why we do this? something todo probably with mustache and dots?
                keys = [str(key) for key in newdata.keys()]
                for key in keys:
                    if key.find(".") != -1:
                        newdata[key.replace(".", "_")] = newdata[key]
                        newdata.pop(key)

                # add new data, this way we get an ever updated dict structure
                self.data.update(newdata)

        def callbackFunctionFile(path, arg):
            self._processFile(path)

        callbackFunctionDir(self.source, "")  # to make sure we use first data.yaml in root

        j.sal.fs.walker.walkFunctional(self.source, callbackFunctionFile=callbackFunctionFile, callbackFunctionDir=callbackFunctionDir, arg="",
                                       callbackForMatchDir=callbackForMatchDir, callbackForMatchFile=callbackForMatchFile)

    def _processFile(self, path):
        content = j.sal.fs.fileGetContents(path)
        self.last_content = content
        self.last_path = path
        self.last_dest = j.sal.fs.joinPaths(j.sal.fs.getDirName(path), j.sal.fs.getBaseName(path)[1:])
        # self.last_dest=j.sal.fs.joinPaths(self.root,j.sal.fs.pathRemoveDirPart(path,self.source))
        # j.sal.fs.createDir(j.sal.fs.getDirName(self.last_dest))

        regex = "\$\{+\w+\(.*\)\}"
        for match in j.data.regex.yieldRegexMatches(regex, content, flags=0):
            methodcode = match.founditem.strip("${}")
            methodcode = methodcode.replace("(", "(self,")

            # find level we are in
            self.last_level = 0
            for line in content.split("\n"):
                if line.find(match.founditem) != -1:
                    # we found position where we are working
                    break
                if line.startswith("#"):
                    self.last_level = len(line.split(" ", 1)[c0].strip())
            try:
                result = eval("self.macros." + methodcode)
            except Exception as e:
                raise e

            # replace return of function
            content = content.replace(match.founditem, result)

        # lets rewrite our style args to mustache style, so we can use both
        regex = "\$\{[a-zA-Z!.]+}"
        for match in j.data.regex.yieldRegexMatches(regex, content, flags=0):
            methodcode = match.founditem.strip("${}").replace(".", "_")
            content = content.replace(match.founditem, "{{%s}}" % methodcode)

        # process multi line blocks
        state = "start"
        block = ""
        out = ""
        for line in content.split("\n"):
            if state == "blockstart" and (line.startswith("```") or line.startswith("'''")):
                # end of block
                line0 = block.split("\n")[0]
                block = "\n".join(block.split("\n")[1:])
                if line0.startswith("!!!"):
                    methodcode = line0[3:]
                    methodcode = methodcode.rstrip(", )")  # remove end )
                    methodcode = methodcode.replace("(", "(self,")
                    methodcode += ",content=block)"
                    methodcode = methodcode.replace(",,", ",")
                    try:
                        block = eval("self.macros." + methodcode)
                    except Exception as e:
                        raise e
                out += block
                block = ""
                state = "start"
                continue

            if state == "blockstart":
                block += "%s\n" % line
                continue

            if state == "start" and (line.startswith("```") or line.startswith("'''")):
                state = "blockstart"
                continue

            out += "%s\n" % line

        content = out

        content = pystache.render(content, self.data)

        j.sal.fs.writeFile(filename=self.last_dest, contents=content)

        # j.data.regex.replace(regexFind, regexFindsubsetToReplace, replaceWith, text)
