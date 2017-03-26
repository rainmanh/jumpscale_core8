from JumpScale import j
from DocSite import DocSite


import imp
import sys
import inspect
import copy


def loadmodule(name, path):
    parentname = ".".join(name.split(".")[:-1])
    sys.modules[parentname] = __package__
    mod = imp.load_source(name, path)
    return mod


caddyconfig = '''

$ws/ {
    root $outpath
    browse
}

$ws/fm/ {
    filemanager / {
        show           $outpath
        allow_new      true
        allow_edit     true
        allow_commands true
        allow_command  git
        allow_command  svn
        allow_command  hg
        allow_command  ls
        block          dotfiles
    }
}

'''


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
        self.docSites = {}  # location in the outpath per site
        self.outpath = j.sal.fs.joinPaths(j.dirs.VARDIR, "docgenerator")
        self.gitRepos = {}
        self.webserver = "http://localhost:1313/"
        self.ws = self.webserver.replace("http://", "").replace("https://", "").replace("/", "")
        self.logger = j.logger.get('docgenerator')

    def addGitRepo(self, path):
        if path not in self.gitRepos:
            gc = j.clients.git.get(path)
            self.gitRepos[path] = gc
        return self.gitRepos[path]

    def installDeps(self):
        if "darwin" in str(j.core.platformtype.myplatform):
            j.do.execute("brew install graphviz")
            j.do.execute("brew install hugo")
            j.do.execute("npm install -g phantomjs")
            j.do.execute("npm install -g mermaid")
            j.do.execute("brew install caddy")
        else:
            raise RuntimeError("only osx supported for now, please fix")

    def startWebserver(self, generateCaddyFile=False):
        """
        start caddy on localhost:1313
        """
        if generateCaddyFile:
            self.generateCaddyFile()
        dest = "%s/docgenerator/caddyfile" % j.dirs.VARDIR
        if not j.sal.fs.exists(dest, followlinks=True):
            self.generateCaddyFile()
        cmd = "ulimit -n 8192;caddy -agree -conf %s" % dest
        self.logger.info("start caddy service, will take 5 sec")
        try:
            sname = j.tools.cuisine.local.tmux.getSessions()[0]
        except:
            sname = "main"
        rc, out = j.tools.cuisine.local.tmux.executeInScreen(sname, "caddy", cmd, reset=True, wait=2)
        if rc > 0:
            raise RuntimeError("Cannot start AYS service")
        self.logger.debug(out)
        self.logger.info("go to %a" % self.webserver)
        return rc, out

    def generateCaddyFile(self):
        dest = "%s/docgenerator/caddyfile" % j.dirs.VARDIR
        out2 = caddyconfig

        C2 = """
        $ws/$name/ {
            root /optvar/docgenerator/$name/public
            #log ../access.log
        }

        """
        for key, ds in self.docSites.items():
            C3 = j.data.text.strip(C2.replace("$name", ds.name))
            out2 += C3
        out2 = out2.replace("$outpath", self.outpath)
        out2 = out2.replace("$ws", self.ws)
        j.sal.fs.writeFile(filename=dest, contents=out2, append=False)

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
            if docDir not in self.docSites:
                print("found doc dir:%s" % docDir)
                ds = DocSite(path=docDir)
                self.docSites[path] = ds
                # self._docRootPathsDone.append(docDir)

    def generateExamples(self, start=True):
        self.load(pathOrUrl="https://github.com/Jumpscale/docgenerator/tree/master/examples")
        self.load(pathOrUrl="https://github.com/Jumpscale/jumpscale_core8/tree/8.2.0")
        self.load(pathOrUrl="https://github.com/Jumpscale/jumpscale_portal8/tree/8.2.0")
        self.generate(start=start)

    def generate(self, start=True):
        if self.docSites == {}:
            self.load()
        for path, ds in self.docSites.items():
            ds.process()
            ds.write()
        self.generateCaddyFile()
        if start:
            self.startWebserver()
        print("TO CHECK GO TO: http://localhost:1313/")

    def gitUpdate(self):
        if self.docSites == {}:
            self.load()
        for gc in self.gitRepos:
            gc.pull()

    def getDoc(self, name, die=True):
        for key, ds in self.docSites.items():
            if name in ds.docs:
                return ds.docs[name]
        if die:
            raise j.exceptions.Input(message="Cannot find doc with name:%s" %
                                     name, level=1, source="", tags="", msgpub="")
        else:
            return None
