from JumpScale import j

def cb():
    from .SpecParser import SpecParserFactory
    return SpecParserFactory()


j.core._register('specparser', cb)
