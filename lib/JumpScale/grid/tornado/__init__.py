from JumpScale import j

def cb():
    from .TornadoFactory import TornadoFactory
    return TornadoFactory()


j.servers._register('tornado', cb)
