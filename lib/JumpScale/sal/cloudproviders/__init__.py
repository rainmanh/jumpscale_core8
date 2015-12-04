from JumpScale import j

def cb():
    from .factory import Factory
    return Factory()


j.tools._register('cloudproviders', cb)

