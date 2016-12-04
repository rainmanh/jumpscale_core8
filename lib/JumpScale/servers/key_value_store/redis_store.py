from servers.key_value_store.store import KeyValueStoreBase
from JumpScale import j

import re

# import time
#
#
# def chunks(l, n):
#     for i in range(0, len(l), n):
#         yield l[i:i + n]


class RedisKeyValueStore(KeyValueStoreBase):

    def __init__(self, name, namespace="db", host='localhost', port=6379, unixsocket=None, db=0, password='', serializers=[], masterdb=None, cache=None, changelog=None):

        self.redisclient = j.clients.redis.get(host, port, password=password, unixsocket=unixsocket)
        # self.redisclient.port = port
        # self.redisclient.host = host
        KeyValueStoreBase.__init__(self, namespace=namespace, name=name, serializers=serializers,
                                   masterdb=masterdb, cache=cache, changelog=changelog)
        self._indexkey = "%s:index" % namespace

        self.inMem = False

    def _getKey(self, key):
        return '%s:%s' % (self.namespace, key)

    def _get(self, key):
        return self.redisclient.get(self._getKey(key))

    def _set(self, key, val, expire=None):
        return self.redisclient.set(self._getKey(key), val, ex=expire)

    def _delete(self, key):
        return self.redisclient.delete(self._getKey(key))

    def _exists(self, key):
        return self.redisclient.exists(self._getKey(key))

    def increment(self, key):
        # only overrule if supporting DB has better ways
        return self.redisclient.incr(self._getKey(key))

    def destroy(self):
        for key in self.redisclient.keys(self.namespace + "*"):
            self.redisclient.delete(key)

    def index(self, items, secret=""):
        """
        @param items is {indexitem:key}
            indexitem is e.g. $actorname:$state:$role (is a text which will be index to key)
            key links to the object in the db
        ':' is not allowed in indexitem
        """
        # if in non redis, implement as e.g. str index in 1 key and if gets too big then create multiple
        for key, val in items.items():
            current_val = self.redisclient.hget(self._indexkey, key)
            if current_val is not None:
                current_val = current_val.decode()
                if val not in current_val.split(','):
                    current_val += "," + val
                    self.redisclient.hset(self._indexkey, key, current_val)
            else:
                self.redisclient.hset(self._indexkey, key, val)
        return True

    def index_remove(self, key, secret=""):
        """
        @param keys is the key to remove from index
        """
        if self.redisclient.hexists(self._indexkey, key):
            self.redisclient.hdel(self._indexkey, key)

    def list(self, regex=".*", returnIndex=False, secret=""):
        """
        regex is regex on the index, will return matched keys
        e.g. .*:new:.* would match all actors with state new
        """
        res = set()
        for item in self.redisclient.hkeys(self._indexkey):
            item = item.decode()
            if re.match(regex, item) is not None:
                key = self.redisclient.hget(self._indexkey, item).decode()
                if returnIndex is False:
                    for key2 in key.split(","):
                        res.add(key2)
                else:
                    for key2 in key.split(","):
                        res.add((item, key2))
        return list(res)

    def _getQueueNameKey(self, name):
        return "%s:queue:%s" % (self.namespace, name)

    def queueSize(self, name):
        """Return the approximate size of the queue."""
        return self.redisclient.llen(self._getQueueNameKey(name))

    def queuePut(self, name, item):
        """Put item into the queue."""
        self.redisclient.rpush(self._getQueueNameKey(name), item)

    def queueGet(self, name, timeout=20):
        """Remove and return an item from the queue."""
        if timeout > 0:
            item = self.redisclient.blpop(self._getQueueNameKey(name), timeout=timeout)
            if item:
                item = item[1]
        else:
            item = self.redisclient.lpop(self._getQueueNameKey(name))
        return item

    def queueFetch(self, name, block=True, timeout=None):
        """ Like get but without remove"""
        if block:
            item = self.redisclient.brpoplpush(self._getQueueNameKey(name), self._getQueueNameKey(name), timeout)
        else:
            item = self.redisclient.lindex(self._getQueueNameKey(name), 0)
        return item

    def lookupSet(self, name, key, fkey):
        self.redisclient.hset(self._indexkey + "lookup", key, fkey)

    def lookupGet(self, name, key):
        self.redisclient.hget(self._indexkey + "lookup", key)

    def lookupDestroy(self, name):
        self.redisclient.delete(self._indexkey + "lookup")

        #
        #     def set(self, category, key, value, expire=0, secret=""):
        #         """
        #         @param expire is in seconds when value will expire
        #         """
        #         if self.hasmaster:
        #             self.writedb.set(category, key, value)
        #             self.addToChangeLog(category, key)  # notify system for change
        #         else:
        #             value = self.serialize(value)
        #
        #             self.redisclient.set(categoryKey, value)
        #
        #     def delete(self, category, key):
        #         if self.hasmaster:
        #             self.writedb.delete(category, key)
        #             self.addToChangeLog(category, key, action='D')
        #         else:
        #             categoryKey = self._getCategoryKey(category, key)
        #             # self._assertExists(categoryKey)
        #             self.redisclient.delete(categoryKey)
        #
        #     def exists(self, category, key):
        #         categoryKey = self._getCategoryKey(category, key)
        #         return self.redisclient.exists(categoryKey)
        #
        #     def increment(self, key):
        #         return self.writedb.redisclient.incr(key)
        #
        #     def list(self, category, prefix):
        #         prefix = "%s:" % category
        #         lprefix = len(prefix)
        #         fullkeys = self.redisclient.keys("%s*" % prefix)
        #         keys = list()
        #         for key in fullkeys:
        #             keys.append(key[lprefix:].decode())
        #         return keys
        #
        #     def listCategories(self):
        #         categories = self.redisclient.keys('*:*')
        #         categories = [category.decode() for category in categories]
        #         return categories
        #
        #     def _getCategoryKey(self, category, key):
        #         if category != "":
        #             return '%s:%s:%s' % (self.namespace, category, key)
        #         elif self.namespace != "":
        #             return '%s:%s' % (self.namespace, key)
        #         else:
        #             return key
        #
        #     # def _stripCategory(self, keys, category):
        #     #     prefix = category + "."
        #     #     nChars = len(prefix)
        #     #     return [key[nChars:] for key in keys]
        #
        #     def _categoryExists(self, category):
        #         categoryKey = self._getCategoryKey(category, "")
        #         return bool(self._client.prefix(categoryKey, 1))
        #
        #     def destroy(self):
        #         self.redisclient.flushdb()
        #
        # # CHANGELOG
        #     def deleteChangeLog(self):
        #         rediscl = self.writedb.redisclient
        #         rediscl.delete(self.lastchangeIdKey)
        #
        #         keys = rediscl.keys("changelog:*")
        #         for chunk in chunks(keys, 100):
        #             rediscl.delete(*chunk)
        #
        #     def checkChangeLog(self):
        #         """
        #         @param reset, will just ignore the changelog
        #         @param delete, means even delete the changelog on master
        #         """
        #         if self.redisclient.get("changelog:lastid") == None:
        #             return
        #         lastid = int(self.redisclient.get("changelog:lastid"))
        #         result = []
        #         if lastid > self.lastchangeId:
        #             try:
        #                 for t in range(self.lastchangeId + 1, lastid + 1):
        #                     self.lastchangeId = t
        #                     key = "changelog:data:%s" % t
        #                     counter = 1
        #                     haskey = self.redisclient.exists(key)
        #                     while not haskey:
        #                         time.sleep(0.05)
        #                         if counter > 10:
        #                             j.events.bug_warning("replication error, did not find key %s" % key, 'osis')
        #                             break
        #                         counter += 1
        #                         haskey = self.redisclient.exists(key)
        #                     if not haskey:
        #                         continue
        #
        #                     epoch, category, key, gid, action = self.redisclient.get(key).split(":", 4)
        #                     if int(gid) == j.application.whoAmI.gid:
        #                         continue
        #                     osis = self.osis[category]
        #                     if action == 'M':
        #                         counter = 1
        #                         key2 = self._getCategoryKey(category, key)
        #                         haskey = self.redisclient.exists(key2)
        #                         while not haskey:
        #                             time.sleep(0.05)
        #                             if counter > 100:
        #                                 j.events.bug_warning("replication error, did not find key %s" % key2, 'osis')
        #                                 break
        #                             counter += 1
        #                             haskey = self.redisclient.exists(key2)
        #                         else:
        #                             obj = osis.get(key)
        #                             if hasattr(obj, 'getDictForIndex'):
        #                                 obj = obj.getDictForIndex()
        #                             osis.index(obj)
        #                     elif action == 'D':
        #                         osis.deleteIndex(key)
        #             finally:
        #                 self.lastchangeId = lastid
        #                 self.writedb.redisclient.set(self.nodelastchangeIdkey, lastid)
        #         return result
        #
        #     def addToChangeLog(self, category, key, action="M"):
        #         if self._changelog and self.hasmaster:
        #             t = self.writedb.redisclient.incr(self.lastchangeIdKey)
        #             self.writedb.redisclient.set("changelog:data:%s" % t, "%s:%s:%s:%s:%s" % (
        #                 int(time.time()), category, key, j.application.whoAmI.gid, action))
