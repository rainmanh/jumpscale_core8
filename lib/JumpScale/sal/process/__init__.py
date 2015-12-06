from JumpScale import j


def cb():
    from .SystemProcess import SystemProcess
    return SystemProcess()


j.sal._register('process', cb)

