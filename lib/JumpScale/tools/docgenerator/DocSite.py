from JumpScale import j
from Doc import *
import copy

import imp
import sys
import inspect
import copy


def loadmodule(name, path):
    parentname = ".".join(name.split(".")[:-1])
    sys.modules[parentname] = __package__
    mod = imp.load_source(name, path)
    return mod


class DocSite:
    """
    """

    def __init__(self, path, yamlPath):
        self.path = path
        self.yamlPath = yamlPath
        self.config = j.data.serializer.yaml.load(yamlPath)
        self.docs = {}

        # now go in configured git directories
        if 'depends' in self.config:
            for url in self.config['depends']:
                path = j.clients.git.getContentPathFromURLorPath(url)
                j.tools.docgenerator.load(path)

        if 'name' not in self.config:
            raise j.exceptions.Input(message="cannot find argument 'name' in config.yaml of %s" %
                                     self.source, level=1, source="", tags="", msgpub="")

        if 'template' not in self.config:
            self.template = "https://github.com/Jumpscale/docgenerator/tree/master/templates/blog"
        else:
            self.template = self.config['template']

        self.templatePath = j.clients.git.getContentPathFromURLorPath(self.template)
        self.generatorPath = j.sal.fs.joinPaths(self.templatePath, "generator.py")

        self.name = self.config["name"].strip().lower()

        # lets make sure its the outpath at this time and not the potentially changing one
        self.outpath = j.sal.fs.joinPaths(copy.copy(j.tools.docgenerator.outpath), self.name)

        self._generator = None

    @property
    def generator(self):
        """
        is the generation code which is in directory of the template, is called generate.py and is in root of template dir
        """
        if self._generator == None:
            self._generator = loadmodule(self.name, self.generatorPath)
        return self._generator

    def write(self):
        j.sal.fs.removeDirTree(self.outpath)
        dest = j.sal.fs.joinPaths(self.outpath, "src")
        j.sal.fs.createDir(dest)
        source = self.path
        j.do.copyTree(source, dest, overwriteFiles=True, ignoredir=['.egg-info', '.dist-info'], ignorefiles=[
                      '.egg-info'], rsync=True, recursive=True, rsyncdelete=False)
        for key, doc in self.docs.items():
            dpath = j.sal.fs.joinPaths(self.outpath, "src", doc.rpath)
            j.sal.fs.createDir(j.sal.fs.getDirName(dpath))
            j.sal.fs.writeFile(filename=dpath, contents=doc.content)
        self.generator.generate(self)
