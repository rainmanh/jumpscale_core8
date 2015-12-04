from JumpScale import j

def cb():
    from .nginx import NginxFactory
    return NginxFactory()


j.sal._register('nginx', cb)
