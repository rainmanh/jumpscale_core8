from JumpScale import j

def cb():
    from .Cache import CacheFactory
    return CacheFactory()


j.tools._register('dbcache', cb)
