from JumpScale import j

def cb():
    from .GoFactory import GoFactory
    return GoFactory()

j.base.loader.makeAvailable(j, 'tools')
j.tools._register('gobuilder', cb)
