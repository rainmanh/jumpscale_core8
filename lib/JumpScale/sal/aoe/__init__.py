from JumpScale import j


def cb():
    from .AOEManager import AOEManager
    return AOEManager()


j.sal._register('aoe', cb)
