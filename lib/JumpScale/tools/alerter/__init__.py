from JumpScale import j

def cb():
    from .AlertService import AlertService
    return AlertService()


j.tools._register('alertservice', cb)
