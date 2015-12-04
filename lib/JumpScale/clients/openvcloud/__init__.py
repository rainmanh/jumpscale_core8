from JumpScale import j

def cb():
    from .openvcloud import OpenvcloudFactory
    return OpenvcloudFactory()


j.clients._register('openvcloud', cb)
