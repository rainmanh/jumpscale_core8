from JumpScale import j


def cb():
    from .Netconfig import Netconfig
    return Netconfig()

j.sal._register('netconfig', cb)
