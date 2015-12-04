from JumpScale import j

def cb():
    from .JumpscriptFactory import JumpscriptFactory
    return JumpscriptFactory()


j.core._register('jumpscripts', cb)
