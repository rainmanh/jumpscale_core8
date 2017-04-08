<!-- toc -->
## j.servers.kvs

- /opt/jumpscale8/lib/JumpScale/servers/key_value_store/StoreFactory.py

### Methods

The key value store factory provides logic to retrieve store instances. It
also caches the stores based on their type, name and namespace.

#### getFSStore(*namespace='', baseDir, serializers*) 

```
Gets a file system key value store.

@param namespace: namespace of the store, defaults to an empty string
@type namespace: String

@param baseDir: base directory of the store, defaults to j.dirs.db
@type namespace: String

@param defaultJSModelSerializer: default JSModel serializer
@type defaultJSModelSerializer: Object

@return: key value store
@rtype: FileSystemKeyValueStore

```

#### getLevelDBStore(*namespace='', basedir, serializers*) 

```
Gets a leveldb key value store.

@param name: name of the store
@type name: String

@param namespace: namespace of the store, defaults to ''
@type namespace: String

@return: key value store

```

#### getMemoryStore(*namespace*) 

```
Gets a memory key value store.

@return: key value store
@rtype: MemoryKeyValueStore

```

#### getRedisStore(*namespace='', host='localhost', port=6379, db, password='', serializers, masterdb, changelog=True*) 

```
Gets a memory key value store.

@param name: name of the store
@type name: String

@param namespace: namespace of the store, defaults to None
@type namespace: String

@return: key value store
@rtype: MemoryKeyValueStore

```

#### getTarantoolDBStore(*namespace='', host='localhost', port=6379, db, password='', serializers*) 

```
Gets a leveldb key value store.

@param name: name of the store
@type name: String

@param namespace: namespace of the store, defaults to ''
@type namespace: String

@return: key value store

```


```
!!!
title = "J Servers Kvs"
date = "2017-04-08"
tags = []
```

```
!!!
title = "J Servers Kvs"
date = "2017-04-08"
tags = []
```

```
!!!
title = "J Servers Kvs"
date = "2017-04-08"
tags = []
```
