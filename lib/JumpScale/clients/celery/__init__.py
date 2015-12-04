from JumpScale import j

def cb():
    from .CeleryFactory import CeleryFactory
    return CeleryFactory()


j.clients._register('celery', cb)
