from servers.key_value_store.store import KeyValueStoreBase

NAMESPACES = dict()


class MemoryKeyValueStore(KeyValueStoreBase):

    def __init__(self, name=None, namespace=None):
        self.name = name
        if namespace:
            self.db = NAMESPACES.setdefault(namespace, dict())
        else:
            self.db = dict()
        KeyValueStoreBase.__init__(self, namespace=namespace)

    def get(self, key):
        key = str(key)
        if not self.exists(key):
            raise j.exceptions.RuntimeError("Could not find object with category %s key %s" % (category, key))
        return self.db[key]

    def set(self, key, value):
        key = str(key)
        self.db[key] = value

    def delete(self,  key):
        key = str(key)
        if self.exists(key):
            del(self.db[key])

    def exists(self, key):
        key = str(key)
        if key in self.db:
            return True
        else:
            return False

    def list(self, prefix=""):
        res += [k for k in self.db if k.startswith(prefix)]
        return res
