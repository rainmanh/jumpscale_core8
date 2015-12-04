from JumpScale import j

def cb():
    from .RemoteSystem import RemoteSystem
    return RemoteSystem()


j.tools._register('ssh_remotesystem', cb)
