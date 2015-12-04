from JumpScale import j

def cb():
    from .ServerBaseFactory import ServerBaseFactory
    return ServerBaseFactory()


j.servers._register('base', cb)
