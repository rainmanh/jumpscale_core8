

from JumpScale import j

def cb():
    from .UnixNetworkManager import UnixNetworkManager
    return UnixNetworkManager()


j.sal._register('nic', cb)