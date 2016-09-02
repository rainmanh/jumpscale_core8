from JumpScale import j

from servers.key_value_store.fs_store import FileSystemKeyValueStore


class StoreFactory:
    '''
    The key value store factory provides logic to retrieve store instances. It
    also caches the stores based on their type, name and namespace.
    '''

    def __init__(self):
        self.__jslocation__ = "j.servers.kvs"
        self._cache = dict()

    # def getMongoDBStore(self, namespace='',serializers=[]):
    #     '''
    #     Gets an MongoDB key value store.

    #     @param namespace: namespace of the store, defaults to None
    #     @type namespace: String

    #     @return: key value store
    #     @rtype: ArakoonKeyValueStore
    #     '''
    #     from mongodb_store import MongoDBKeyValueStore
    #     key = '%s_%s' % ("arakoon", namespace)
    #     if key not in self._cache:
    #         if namespace=="":
    #             namespace="main"
    #         self._cache[key] = MongoDBKeyValueStore(namespace)
    #     return self._cache[key]

    def test(self):
        cache = j.servers.kvs.getRedisCacheLocal()
        serializer = j.data.serializer.json
        db = j.servers.kvs.getRedisStore(namespace="testdb", serializers=[serializer], cache=cache)
        obj = [1, 2, 3, 4]
        db.set("mykey", obj)
        assert db.get("mykey") == obj

        # TODO: do same with category and some other args

    def getRedisCacheLocal(self):
        """
        example:
        cache=j.servers.kvs.getRedisCacheLocal()
        serializer=j.data.serializer.json
        db=j.servers.kvs.getRedisStore(namespace="testdb",serializers=[serializer],cache=cache)

        """
        # for now just local to test
        cache = self.getRedisStore(namespace='cache', host='localhost', port=6379, db=0,
                                   password='', serializers=[])
        return cache

    # def getFSStore(self, name, namespace='', baseDir=None, serializers=[], cache=None, changelog=None, masterdb=None):
    #     '''
    #     Gets a file system key value store.
    #
    #     @param namespace: namespace of the store, defaults to an empty string
    #     @type namespace: String
    #
    #     @param baseDir: base directory of the store, defaults to j.dirs.db
    #     @type namespace: String
    #
    #     @param defaultJSModelSerializer: default JSModel serializer
    #     @type defaultJSModelSerializer: Object
    #
    #     @return: key value store
    #     @rtype: FileSystemKeyValueStore
    #     '''
    #
    #     if serializers == []:
    #         serializers = [j.data.serializer.serializers.getMessagePack()]
    #
    #     if name not in self._cache:
    #         self._cache[name] = FileSystemKeyValueStore(
    #             name, namespace=namespace, baseDir=baseDir, serializers=serializers, cache=cache, masterdb=masterdb, changelog=changelog)
    #     return self._cache[name]
    #
    # def getMemoryStore(self, name, namespace=None, changelog=None):
    #     '''
    #     Gets a memory key value store.
    #
    #     @return: key value store
    #     @rtype: MemoryKeyValueStore
    #     '''
    #     from servers.key_value_store.memory_store import MemoryKeyValueStore
    #     return MemoryKeyValueStore(name=name, namespace=namespace, changelog=changelog)
    #
    def getRedisStore(self, name, namespace='', host='localhost', port=6379, db=0, password='',
                      serializers=None, masterdb=None, cache=None, changelog=None):
        '''
        Gets a memory key value store.

        @param name: name of the store
        @type name: String

        @param namespace: namespace of the store, defaults to None
        @type namespace: String

        @return: key value store
        @rtype: MemoryKeyValueStore
        '''
        from servers.key_value_store.redis_store import RedisKeyValueStore
        if name not in self._cache:
            self._cache[name] = RedisKeyValueStore(namespace=namespace, host=host, port=port, db=db,
                                                   password=password, serializers=serializers, masterdb=masterdb, changelog=changelog, cache=cache)
        return self._cache[name]

    # def getLevelDBStore(self, name, namespace='', basedir=None, serializers=[], cache=None, changelog=None, masterdb=None):
    #     '''
    #     Gets a leveldb key value store.
    #
    #     @param name: name of the store
    #     @type name: String
    #
    #     @param namespace: namespace of the store, defaults to ''
    #     @type namespace: String
    #
    #     @return: key value store
    #     '''
    #     from servers.key_value_store.leveldb_store import LevelDBKeyValueStore
    #     if name not in self._cache:
    #         self._cache[name] = LevelDBKeyValueStore(
    #             name=name, namespace=namespace, basedir=basedir, serializers=serializers, cache=cache, masterdb=masterdb, changelog=changelog)
    #     return self._cache[name]

    # def getTarantoolDBStore(self, name, namespace='', host='localhost', port=6379, db=0, password='', serializers=[], cache=None, changelog=None, masterdb=None):
    #     '''
    #     Gets a leveldb key value store.
    #
    #     @param name: name of the store
    #     @type name: String
    #
    #     @param namespace: namespace of the store, defaults to ''
    #     @type namespace: String
    #
    #     @return: key value store
    #     '''
    #     from servers.key_value_store.tarantool_store import TarantoolStore
    #     if name not in self._cache:
    #         self._cache[name] = TarantoolStore(namespace=namespace, host='localhost',
    #                                            port=6379, db=0, password='', serializers=serializers, cache=cache, masterdb=masterdb, changelog=changelog)
    #     return self._cache[name]
