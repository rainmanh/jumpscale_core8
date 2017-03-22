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

        from IPython import embed
        embed()
        raise RuntimeError("stop debug here")

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
            yamlfile = j.sal.fs.joinPaths(path, "generate.yaml")
            if j.sal.fs.exists(yamlfile):
                self.docSiteLast = DocSite(yamlfile)
                self.docSites[self.docSiteLast.name] = self.docSiteLast

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
            ext = j.sal.fs.getFileExtension(path)
            base = j.sal.fs.getBaseName(path).lower()
            if ext == "md":
                base = base[:-3]  # remove extension
                if base not in self.docs:
                    self.docs[base] = Doc(path, base, docSite=self.docSiteLast)
                    self.docs[base].data = copy.copy(self.data)

        callbackFunctionDir(self.path, "")  # to make sure we use first data.yaml in root

        j.sal.fs.walker.walkFunctional(self.path, callbackFunctionFile=callbackFunctionFile,
                                       callbackFunctionDir=callbackFunctionDir, arg="",
                                       callbackForMatchDir=callbackForMatchDir, callbackForMatchFile=callbackForMatchFile)
