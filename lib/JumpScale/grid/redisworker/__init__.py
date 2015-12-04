from JumpScale import j

def cb():
    from .RedisWorker import RedisWorkerFactory
    return RedisWorkerFactory()


j.clients._register('redisworker', cb)


