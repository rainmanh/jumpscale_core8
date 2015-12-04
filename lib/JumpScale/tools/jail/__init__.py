from JumpScale import j

def cb():
    from .JailFactory import JailFactory
    return JailFactory()


j.tools._register('jail', cb)
