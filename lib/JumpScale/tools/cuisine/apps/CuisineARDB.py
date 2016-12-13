from JumpScale import j


app = j.tools.cuisine._getBaseAppClass()


# IS ONLY PRIO 2 !!!

class CuisineARDB(app):
    NAME = 'ardb'

    def build(self, reset=False):
        raise NotImplementedError()

    def buildForestDB(self):
        # build python extension as well a C parts
        self.cuisine.run("apt-get install libsnappy-dev")
        raise NotImplementedError

    def installForestDB(self):
        # copy to right locations in sandbox
        raise NotImplementedError

    def install(self, reset=False):
        """
        as backend use ForestDB
        """
        raise NotImplementedError

    def start(self, name="main", ip="localhost", port=6379, maxram=200, appendonly=True,
              snapshot=False, slave=(), ismaster=False, passwd=None):
        raise NotImplementedError

    def test(self):
        """
        install on top of forestdb
        do some test through normal redis client
        """
        raise NotImplementedError
