from JumpScale import j


def cb():
    from .SystemFS import SystemFS
    return SystemFS()


j.sal._register('fs', cb)
j.system._register('fs', cb)


