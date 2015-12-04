from JumpScale import j

def cb():
    from .SSLSigning import SSLSigning
    return SSLSigning()


j.sal._register('ssl_signing', cb)
