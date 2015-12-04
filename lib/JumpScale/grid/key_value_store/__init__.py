from JumpScale import j

def cb():
    from .store_factory import KeyValueStoreFactory
    return KeyValueStoreFactory()


j.servers._register('keyvaluestore', cb)
