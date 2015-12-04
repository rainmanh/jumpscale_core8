from JumpScale import j

def cb():
    from .Lock import Lock
    return Lock()


j.tools._register('lock', cb)
