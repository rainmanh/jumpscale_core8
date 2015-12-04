from JumpScale import j

def cb():
    from .SSL import SSL
    return SSL()


j.sal._register('ssl', cb)
