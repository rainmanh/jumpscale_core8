from JumpScale import j

def cb():
    from .NetConfigFactory import NetConfigFactory
    return NetConfigFactory()


j.sal._register('openvswitch', cb)

