
from JumpScale import j


class AtYourServiceDBFactory():

    def get(self, name):
        return AtYourServiceDB(name)


class AtYourServiceDB():

    def __init__(self, category):
        self.db = j.servers.kvs.getRedisStore("ays", changelog=False)

    def set(self, key, obj):
        from IPython import embed
        print("DEBUG NOW set")
        embed()

    def get(self, key):
        from IPython import embed
        print("DEBUG NOW get")
        embed()

    def delete(self, key):
        from IPython import embed
        print("DEBUG NOW delete")
        embed()

    def increment(self, key):
        from IPython import embed
        print("DEBUG NOW increment")
        embed()

    def destroy(self):
        from IPython import embed
        print("DEBUG NOW destroy")
        embed()
