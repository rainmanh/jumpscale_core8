from JumpScale import j


def systemFS():
    from .SystemFS import SystemFS
    return SystemFS()

def systemFSWalker():
    from .SystemFSWalker import SystemFSWalker
    return SystemFSWalker()

j.sal._register('fs', systemFS)
j.sal._register('fswalker', systemFSWalker)
# j.system._register('fs', cb)


