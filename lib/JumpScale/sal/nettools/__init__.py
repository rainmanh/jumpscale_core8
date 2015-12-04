from JumpScale import j


def cb():
    from .NetTools import NetTools
    return NetTools()


j.sal._register('nettools', cb)

