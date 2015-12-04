from JumpScale import j

def cb():
    from .DiskManager import DiskManager
    return DiskManager()


j.sal._register('disklayout', cb)