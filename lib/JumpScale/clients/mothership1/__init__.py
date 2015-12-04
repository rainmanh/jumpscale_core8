from JumpScale import j

def cb():
    from .ms1 import MS1Factory
    return MS1Factory()


# j.tools._register('ms1', cb)
j.clients._register('mothership1', cb)