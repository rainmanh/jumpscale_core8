from JumpScale import j


app = j.tools.cuisine._getBaseAppClass()


# IS ONLY PRIO 2 !!!

class CuisineARDB(app):
    NAME = 'ardb'

    def build(self, reset=False):
        raise NotImplementedError()

    def buildForestDB(self):

    def installForestDB(self):

    def install(self, reset=False):
        """
        as backend use ForestDB
        """

    def start(self, name="main", ip="localhost", port=6379, maxram=200, appendonly=True,
              snapshot=False, slave=(), ismaster=False, passwd=None):

    def test(self):
        """
        install on top of forestdb
        do some test through normal redis client
        """
