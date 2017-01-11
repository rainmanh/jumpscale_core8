from servers.key_value_store.store import KeyValueStoreBase

NAMESPACES = dict()

import re


class MemoryKeyValueStore(KeyValueStoreBase):

    def __init__(self, name=None, namespace=None):
        self.name = name
        if namespace:
            self.db = NAMESPACES.setdefault(namespace, dict())
        else:
            self.db = dict()
        KeyValueStoreBase.__init__(self, namespace=namespace)
        self.dbindex = dict()
        self.lookup = dict()
        self.inMem = True

    def get(self, key, secret=""):
        key = str(key)
        if not self.exists(key):
            raise j.exceptions.RuntimeError("Could not find object with category %s key %s" % (self.category, key))
        return self.db[key]

    def getraw(self, key, secret="", die=False, modecheck="r"):
        key = str(key)
        if not self.exists(key):
            if die == False:
                return None
            else:
                raise j.exceptions.RuntimeError("Could not find object with category %s key %s" % (self.category, key))
        return self.db[key]

    def set(self, key, value, secret=""):
        key = str(key)
        self.db[key] = value

    def delete(self,  key, secret=""):
        key = str(key)
        if self.exists(key):
            del(self.db[key])

    def exists(self, key, secret=""):
        key = str(key)
        if key in self.db:
            return True
        else:
            return False

    def index(self, items, secret=""):
        """
        @param items is {indexitem:key}
            indexitem is e.g. $actorname:$state:$role (is a text which will be index to key)
                indexitems are always made lowercase
            key links to the object in the db
        ':' is not allowed in indexitem
        """
        self.dbindex.update(items)

    def index_remove(self, keys, secret=""):
        self.dbindex = {}

    def list(self, regex=".*", returnIndex=False, secret=""):
        """
        regex is regex on the index, will return matched keys
        e.g. .*:new:.* would match e.g. all obj with state new
        """

        res = set()
        for item, key in self.dbindex.items():
            if re.match(regex, item) is not None:
                if returnIndex is False:
                    for key2 in key.split(","):
                        res.add(key2)
                else:
                    for key2 in key.split(","):
                        res.add((item, key2))
        return list(res)

    def lookupSet(self, name, key, fkey):
        if name not in self.lookup:
            self.lookup[name] = {}
        self.lookup[name][key] = fkey

    def lookupGet(self, name, key):
        if name not in self.lookup:
            return None
        if key in self.lookup[name]:
            return self.lookup[name][key]
        else:
            return None

    def lookupDestroy(self, name):
        self.lookup.pop(name)
