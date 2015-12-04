from JumpScale import j

def cb():
    from .OauthFactory import OauthFactory
    return OauthFactory()


j.clients._register('oauth', cb)
