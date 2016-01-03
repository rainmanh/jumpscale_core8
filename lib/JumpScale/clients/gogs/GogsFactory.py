from GitClient import GitClient
from JumpScale import j
import os


class GitFactory:
    def __init__(self):
        self.__jslocation__ = "j.clients.gogs"
        j.logger.consolelogCategories.append("gogs")

    def get(self, basedir):
        """
        see https://gogs.io/
        """
        return GitClient(basedir)

    def log(self, msg, category="", level=5):
        category = "gogs.%s" % category
        category = category.rstrip(".")
        j.logger.log(msg, category=category, level=level)

