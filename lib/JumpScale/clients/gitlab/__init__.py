from JumpScale import j

def cb():
    from .GitlabFactory import GitlabFactory
    return GitlabFactory()


j.clients._register('gitlab', cb)
