from JumpScale import j

def cb():
    from .Time_ import Time_
    return Time_()


j.tools._register('time', cb)
