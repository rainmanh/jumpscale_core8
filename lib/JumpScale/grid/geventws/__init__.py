from JumpScale import j

def cb():
    from .GeventWSFactory import GeventWSFactory
    return GeventWSFactory()


j.servers._register('geventws', cb)
