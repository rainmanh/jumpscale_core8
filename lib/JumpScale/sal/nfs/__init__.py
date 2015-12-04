from JumpScale import j

def cb():
    from .NFS import NFS
    return NFS()


j.sal._register('nfs', cb)