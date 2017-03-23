from JumpScale import j
from DocSource import DocSource


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
    optionally call pdf gitbook generator to produce pdf(s)
    """

    def __init__(self):
        self.__jslocation__ = "j.tools.docgenerator"
        self._macroPathsDone = []
        self._initOK = False
        self._macroCodepath = j.sal.fs.joinPaths(j.dirs.VARDIR, "docgenerator_internal", "macros.py")
        j.sal.fs.createDir(j.sal.fs.joinPaths(j.dirs.VARDIR, "docgenerator_internal"))
        self._docRootPathsDone = []
        self.docSources = {}  # where the docs come from
        self.docSites = {}  # location in the outpath per site
        self.outpath = j.sal.fs.joinPaths(j.dirs.VARDIR, "docgenerator")
        self.gitRepos = {}

    def addGitRepo(self, path):
        if path not in self.gitRepos:
            gc = j.clients.git.get(path)
            self.gitRepos[path] = gc
        return self.gitRepos[path]

    def installDeps(self):
        if "darwin" in j.core.platformtype.myplatform:
            j.do.execute("brew install graphviz")
            j.do.execute("brew install hugo")
            j.do.execute("npm install -g phantomjs")
            j.do.execute("npm install -g mermaid")
        else:
            raise RuntimeError("only osx supported for now, please fix")

    def init(self):
        if self._initOK == False:
            j.sal.fs.remove(self._macroCodepath)
        # load the default macro's
        self.loadMacros("https://github.com/Jumpscale/docgenerator/tree/master/macros")

    def loadMacros(self, pathOrUrl=""):
        """
        @param pathOrUrl can be existing path or url
        e.g. https://github.com/Jumpscale/docgenerator/tree/master/examples
        """

        path = j.clients.git.getContentPathFromURLorPath(pathOrUrl)

        if path not in self._macroPathsDone:

            if not j.sal.fs.exists(path=path):
                raise j.exceptions.Input("Cannot find path:'%s' for macro's, does it exist?" % path)

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

            self._macroPathsDone.append(path)

    def load(self, pathOrUrl=""):
        """
        will look for config.yaml in $source/config.yaml

        @param pathOrUrl is the location where the markdown docs are which need to be processed
            if not specified then will look for root of git repo and add docs
            source = $gitrepoRootDir/docs

            this can also be a git url e.g. https://github.com/Jumpscale/docgenerator/tree/master/examples

        """
        self.init()
        if pathOrUrl == "":
            path = j.sal.fs.getcwd()
            path = j.clients.git.findGitPath(path)
        else:
            path = j.clients.git.getContentPathFromURLorPath(pathOrUrl)

        for docDir in j.sal.fs.listFilesInDir(path, True, filter=".docs"):
            if docDir not in self.docSources:
                print("found doc dir:%s" % docDir, sep=' ', end='n', file=sys.stdout, flush=False)
                ds = DocSource(path=docDir)
                self.docSources[path] = ds
                # self._docRootPathsDone.append(docDir)

    def generateExamples(self):
        self.load(pathOrUrl="https://github.com/Jumpscale/docgenerator/tree/master/examples")
        self.load(pathOrUrl="https://github.com/Jumpscale/jumpscale_core8/tree/8.2.0")
        self.load(pathOrUrl="https://github.com/Jumpscale/jumpscale_portal8/tree/8.2.0")
        self.generate()

    def generate(self):
        if self.docSites == {}:
            self.load()
        for path, ds in self.docSources.items():
            ds.process()
        for key, ds in self.docSites.items():
            ds.write()

    def gitUpdate(self):
        if self.docSites == {}:
            self.load()
        for gc in self.gitRepos:
            gc.pull()
