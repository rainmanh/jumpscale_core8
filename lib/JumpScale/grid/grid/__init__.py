from JumpScale import j

def cb():
    from .GridFactory import GridFactory
    return GridFactory()


j.core._register('grid', cb)
