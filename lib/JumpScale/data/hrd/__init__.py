from JumpScale import j

def cb():
    from .HRDFactory import HRDFactory
    return HRDFactory()

j.data._register('hrd', cb)
