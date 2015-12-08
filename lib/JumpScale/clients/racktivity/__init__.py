from JumpScale import j

def cb():
    from .RacktivityFactory import RacktivityFactory
    return RacktivityFactory()


j.clients._register('racktivity', cb)
