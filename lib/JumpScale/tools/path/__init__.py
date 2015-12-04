from JumpScale import j

def cb():
    from .PathFactory import PathFactory
    return PathFactory()


j.tools._register('path', cb)
