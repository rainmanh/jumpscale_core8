from JumpScale import j
from Doc import *
import copy


class DocSite:
    """
    """

    def __init__(self, yamlPath):
        self.yamlPath = yamlPath
        self.config = j.data.serializer.yaml.load(yamlPath)

        # now go in configured git directories
        if 'depends' in self.config:
            for url in self.config['depends']:
                repository_url, gitpath, relativepath = j.clients.git.getContentPathFromURL(url)
                path = j.sal.fs.joinPaths(gitpath, relativepath)
                j.tools.docgenerator.load(path)

        if 'name' not in self.config:
            raise j.exceptions.Input(message="cannot find argument 'name' in config.yaml of %s" %
                                     self.source, level=1, source="", tags="", msgpub="")

        self.name = self.config["name"].strip().lower()

        # lets make sure its the outpath at this time and not the potentially changing one
        self.outpath = copy.copy(j.tools.docgenerator.outpath)
