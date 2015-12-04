from JumpScale import j

def cb():
    from .UFWManager import UFWManager
    return UFWManager()


j.sal._register('ufw', cb)