from JumpScale import j

def cb():
    from .Redis2 import RedisFactory
    return RedisFactory()


j.clients._register('redis', cb)
