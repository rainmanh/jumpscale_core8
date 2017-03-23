from JumpScale import j
from Doc import *
import copy


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

        self.name = self.config["name"].strip().lower()

        # lets make sure its the outpath at this time and not the potentially changing one
        self.outpath = copy.copy(j.tools.docgenerator.outpath)

    def write(self):
        from IPython import embed
        print("DEBUG NOW iuiu")
        embed()
        raise RuntimeError("stop debug here")
        for key, doc in self.docs.items():
            j.sal.fs.joinPaths(self.path, doc.rpath)
            j.sal.fs.writeFile(filename=dpath, contents=doc.content)
