from JumpScale import j

base = j.tools.cuisine._getBaseClass()


class CuisineRocksDB(base):
    def install(self):
        self.cuisine.package.install("librocksdb-dev")
        self.cuisine.package.install("libhiredis-dev")
        self.cuisine.package.install("libbz2-dev")

        self.cuisine.development.pip.multiInstall(['pyrocksdb', 'peewee'])
