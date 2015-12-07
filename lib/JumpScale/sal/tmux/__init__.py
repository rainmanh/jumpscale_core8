from JumpScale import j

def cb():
    from .AppManager import AppManager
    return AppManager()


j._register('apps', cb)
