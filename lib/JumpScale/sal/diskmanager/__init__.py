from JumpScale import j

def cb():
    from .Diskmanager import Diskmanager
    return Diskmanager()


j.sal._register('diskmanager', cb)

