from JumpScale import j


def cb():
    from .Ubuntu import Ubuntu
    return Ubuntu()


j.sal._register('ubuntu', cb)
