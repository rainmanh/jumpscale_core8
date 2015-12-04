from JumpScale import j

def cb():
    from JumpScale.grid.osis2.factory import ClientFactory
    return ClientFactory()



j.clients._register('osis2', cb)
