from JumpScale import j

def cb():
    from .CRedis import CRedisFactory
    return CRedisFactory()


j.clients._register('credis', cb)


