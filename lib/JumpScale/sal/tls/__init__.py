from JumpScale import j

def cb():
    from .TLSFactory import TLSFactory
    return TLSFactory()


j.tools._register('tls', cb)