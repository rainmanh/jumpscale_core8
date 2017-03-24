from JumpScale import j
from Doc import Doc
from DocSite import DocSite
import copy


class DocSource:
    """
    """

    def __init__(self, path=""):
        self.path = j.sal.fs.getDirName(path)

        gitpath = j.clients.git.findGitPath(path)

        self.git = j.tools.docgenerator.addGitRepo(gitpath)

        self.data = {}
        self.docSiteLast = None
        self.docSites = {}
        self.docs = {}

        self.load()

        self._defaultContent = None

    @property
    def defaultContent(self):
        if self._defaultContent == None:
            path = "%s/default.md" % self.path
            if j.sal.fs.exists(path, followlinks=True):
                self._defaultContent = j.sal.fs.fileGetContents(path)
            else:
                self._defaultContent = ""
        return self._defaultContent

    def load(self):
        """
        walk in right order over all files which we want to potentially use (include)
        and remember their paths

        if duplicate only the first found will be used

        """
        path = self.path
        if not j.sal.fs.exists(path=path):
            raise j.exceptions.NotFound("Cannot find source path in load:'%s'" % path)

        def callbackForMatchDir(path, arg):
            base = j.sal.fs.getBaseName(path)
            if base.startswith("."):
                return False

            # check if we find a macro dir, if so load
            if base == "macros":
                j.tools.docgenerator.loadMacros(path=path)

            return True

        def callbackForMatchFile(path, arg):
            base = j.sal.fs.getBaseName(path).lower()
            if base.startswith("_"):
                return False
            if not j.sal.fs.getFileExtension(path) in ["md", "yaml"]:
                return False
            base = base[:-3]  # remove extension
            if base in ["summary"]:
                return False
            return True

        def callbackFunctionDir(path, arg):

            # need to do this here because the md's need to be processed in next step
            yamlfile = j.sal.fs.joinPaths(path, "config.yaml")
            if j.sal.fs.exists(yamlfile):
                self.docSiteLast = DocSite(path=path, yamlPath=yamlfile)
                self.docSites[self.docSiteLast.name] = self.docSiteLast
                j.tools.docgenerator.docSites[self.docSiteLast.name] = self.docSiteLast

            yamlfile = j.sal.fs.joinPaths(path, "data.yaml")
            if j.sal.fs.exists(yamlfile):
                newdata = j.data.serializer.yaml.load(yamlfile)

                if not j.data.types.dict.check(newdata):
                    raise j.exceptions.Input(message="cannot process yaml on path:%s, needs to be dict." %
                                             yamlfile, level=1, source="", tags="", msgpub="")

                # dont know why we do this? something todo probably with mustache and dots?
                keys = [str(key) for key in newdata.keys()]
                for key in keys:
                    if key.find(".") != -1:
                        newdata[key.replace(".", "_")] = newdata[key]
                        newdata.pop(key)

                # add new data, this way we get an ever updated dict structure
                self.data.update(newdata)

        def callbackFunctionFile(path, arg):
            ext = j.sal.fs.getFileExtension(path)
            base = j.sal.fs.getBaseName(path).lower()
            if ext == "md":
                base = base[:-3]  # remove extension
                if base not in self.docs:
                    self.docs[base] = Doc(path, base, docSource=self)
                    self.docs[base].data = copy.copy(self.data)
                    self.docSiteLast.docs[base] = self.docs[base]

        callbackFunctionDir(self.path, "")  # to make sure we use first data.yaml in root

        j.sal.fs.walker.walkFunctional(self.path, callbackFunctionFile=callbackFunctionFile,
                                       callbackFunctionDir=callbackFunctionDir, arg="",
                                       callbackForMatchDir=callbackForMatchDir, callbackForMatchFile=callbackForMatchFile)

    def process(self):
        for key, doc in self.docs.items():
            doc.process()
