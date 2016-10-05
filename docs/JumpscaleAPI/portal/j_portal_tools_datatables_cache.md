<!-- toc -->
## j.portal.tools.datatables.cache

- /opt/jumpscale8/lib/JumpScale/servers/key_value_store/memory_store.py
- Properties
    - db
    - serializers
    - unserializers
    - logger

### Methods

#### cacheDelete(*key*) 

#### cacheExists(*key*) 

#### cacheExpire() 

#### cacheGet(*key, deleteAfterGet*) 

#### cacheList() 

#### cacheSet(*key, value, expirationInSecondsFromNow=60*) 

#### checkChangeLog() 

#### delete(*category, key*) 

```
Deletes a key value pair from the store.

@param: category of the key value pair
@type: String

@param: key of the key value pair
@type: String

```

#### exists(*category, key*) 

```
Checks if a key value pair exists in the store.

@param: category of the key value pair
@type: String

@param: key of the key value pair
@type: String

@return: flag that states if the key value pair exists or not
@rtype: Boolean

```

#### get(*category, key*) 

```
Gets a key value pair from the store.

@param: category of the key value pair
@type: String

@param: key of the key value pair
@type: String

@return: value of the key value pair
@rtype: Objects

```

#### getModifySet(*category, key, modfunction, **kwargs*) 

```
get value
give as parameter to modfunction
try to set by means of testset, if not succesfull try again, will use random function to
    maximize chance to set
@param kwargs are other parameters as required (see usage in subscriber function)

```

#### getNrRecords(*incrementtype*) 

#### get_dedupe(*category, key*) 

#### increment(*incrementtype*) 

```
@param incrementtype : type of increment is in style machine.disk.nrdisk  (dot notation)

```

#### incrementReset(*incrementtype, newint*) 

```
@param incrementtype : type of increment is in style machine.disk.nrdisk  (dot notation)

```

#### list(*category='', prefix=''*) 

```
Lists the keys matching `prefix` in `category`.

@param category: category the keys should be in
@type category: String
@param prefix: prefix the keys should start with
@type prefix: String
@return: keys that match `prefix` in `category`.
@rtype: List(String)

```

#### listCategories() 

```
Lists the categories in this db.

@return: categories in this db
@rtype: List(String)

```

#### lock(*locktype, info='', timeout=5, timeoutwait, force*) 

```
if locked will wait for time specified
@param locktype of lock is in style machine.disk.import  (dot notation)
@param timeout is the time we want our lock to last
@param timeoutwait wait till lock becomes free
@param info is info which will be kept in lock, can be handy to e.g. mention why lock
    taken
@param force, if force will erase lock when timeout is reached
@return None

```

#### lockCheck(*locktype*) 

```
@param locktype of lock is in style machine.disk.import  (dot notation)
@return result,id,lockEnd,info  (lockEnd is time when lock times out, info is descr of
    lock, id is who locked)
               result is False when free, True when lock is active

```

#### now() 

```
return current time

```

#### serialize(*value*) 

#### set(*category, key, value*) 

```
Sets a key value pair in the store.

@param: category of the key value pair
@type: String

@param: key of the key value pair
@type: String

```

#### set_dedupe(*category, data*) 

```
will return unique key which references the data, if it exists or not

```

#### settest(*category, key, value*) 

```
if well stored return True

```

#### subscribe(*subscriberid, category, startid*) 

```
each subscriber is identified by a key
in db there is a dict stored on key for category = category of this method
value= dict with as keys the subscribers
\{"kristof":[lastaccessedTime,lastId],"pol":...\}

```

#### subscriptionAdvance(*subscriberid, category, lastProcessedId*) 

#### subscriptionGetNextItem(*subscriberid, category, autoConfirm=True*) 

```
get next item from subscription
returns
   False,None when no next
   True,the data when a next

```

#### unlock(*locktype, timeoutwait, force*) 

```
@param locktype of lock is in style machine.disk.import  (dot notation)

```

#### unserialize(*value*) 

