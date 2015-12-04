from JumpScale import j

def cb():
    from .Sandboxer import Sandboxer
    return Sandboxer()


j.tools._register('sandboxer', cb)

