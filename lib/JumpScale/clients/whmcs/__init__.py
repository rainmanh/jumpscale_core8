from JumpScale import j

def cb():
    from .WhmcsFactory import WhmcsFactory
    return WhmcsFactory()


j.clients._register('whmcs', cb)

