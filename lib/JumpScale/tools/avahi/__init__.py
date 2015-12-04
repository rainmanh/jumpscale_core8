from JumpScale import j

def cb():
    from .Avahi import Avahi
    return Avahi()


j.tools._register('avahi', cb)
