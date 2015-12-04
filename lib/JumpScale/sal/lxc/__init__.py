from JumpScale import j

def cb():
    from .Lxc import Lxc
    return Lxc()


j.sal._register('lxc', cb)

