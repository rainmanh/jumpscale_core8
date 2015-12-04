from JumpScale import j

def cb():
    from .RegexTools import RegexTools
    return RegexTools()


j.tools._register('regex', cb)
