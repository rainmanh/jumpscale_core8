from JumpScale import j

def cb():
    from .Time_ import Time
    return Time


j.tools._register('time', cb)
