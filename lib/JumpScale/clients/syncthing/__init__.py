from JumpScale import j

def cb():
    from .Syncthing import Syncthing
    return Syncthing()


j.clients._register('syncthing', cb)


