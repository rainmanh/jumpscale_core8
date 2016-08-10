
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

    def get(self, key):
        return self.db.get(self.category, key)

    def delete(self, key):
        self.db.delete(self.category, key)

    def increment(self, key):
        return self.db.increment(key)

    def destroy(self):
        self.db.destroy()

    def exists(self, key):
        return self.db.exists(self.category, key)

    def getQueue(self, queue):
        return self.db.redisclient.getQueue(queue)

    def hset(self, name, key, value):
        # is not compatible with other kvs's. Not good. Rethink
        self.db.redisclient.hset(name, key, value)
        return True

    def hget(self, name, key):
        # is not compatible with other kvs's. Not good. Rethink
        return self.db.redisclient.hget(name, key)
