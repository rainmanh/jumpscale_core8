from JumpScale import j

def cb():
    from .GeventLoopFactory import GeventLoopFactory
    return GeventLoopFactory()


j.core._register('gevent', cb)
