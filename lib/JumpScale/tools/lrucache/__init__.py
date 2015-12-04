from JumpScale import j

def cb():
    from .LRUCacheFactory import LRUCacheFactory
    return LRUCacheFactory()


j.servers._register('cachelru', cb)


