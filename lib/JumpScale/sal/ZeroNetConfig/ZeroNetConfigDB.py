
from JumpScale import j

import capnp

import zernoNetConfigModel_capnp as ZeroNetConfigModel

# class ZeroNetConfigDBFactory():
#
#     def get(self, name):
#         return AtYourServiceDB(name)


class ZeroNetConfigDB():

    def __init__(self, category):
        self.db = j.servers.kvs.getRedisStore("0netconfig", changelog=False)

    def set(self, key, obj):
        from IPython import embed
        print("DEBUG NOW set")
        embed()

    def get(self, key):
        from IPython import embed
        print("DEBUG NOW set")
        embed()

    def delete(self, key):
        from IPython import embed
        print("DEBUG NOW set")
        embed()
