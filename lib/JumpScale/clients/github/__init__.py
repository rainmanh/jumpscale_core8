from JumpScale import j

def cb():
    from .github import GitHubFactory
    return GitHubFactory()


j.clients._register('github', cb)
