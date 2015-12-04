from JumpScale import j

def cb():
    from .HTMLFactory import HTMLFactory
    return HTMLFactory()


j.tools._register('html', cb)

