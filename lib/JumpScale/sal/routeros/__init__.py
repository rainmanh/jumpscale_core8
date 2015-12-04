from JumpScale import j

def cb():
    from .RouterOS import RouterOSFactory
    return RouterOSFactory()


j.sal._register('routeros', cb)
