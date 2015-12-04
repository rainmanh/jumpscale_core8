from JumpScale import j

def cb():
    from .TipcFactory import TipcFactory
    return TipcFactory()


j.servers._register('tipc', cb)
