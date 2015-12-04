from JumpScale import j


def cb():
    from .HostFile import HostFile
    return HostFile()


j.sal._register('hostfile', cb)

