from JumpScale import j

def cb():
    from .GitFactory import GitFactory
    return GitFactory()


j.clients._register('git', cb)

