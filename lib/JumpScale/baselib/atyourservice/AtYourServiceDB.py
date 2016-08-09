
from JumpScale import j


class AtYourServiceDBFactory():

    def get(self, name):
        return AtYourServiceDB(name)


class AtYourServiceDB():

    def __init__(self, category):
        self.category = category
        self.db = j.servers.kvs.getRedisStore("ays", changelog=False)

    def set(self, key, obj):
        self.db.set(self.category, key, obj)

    def set(self, category, key, obj):
        self.db.set(category, key, obj)

    def get(self, key):
        return self.db.get(self.category, key)

    def delete(self, key):
        self.db.delete(self.category, key)

    def increment(self, key):
        self.db.increment(key)

    def destroy(self):
        from IPython import embed
        print("DEBUG NOW destroy")
        embed()
