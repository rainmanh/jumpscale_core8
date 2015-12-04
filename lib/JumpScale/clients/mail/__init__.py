from JumpScale import j

def cb():
    from .emailclient import EmailClient
    return EmailClient()


j.clients._register('email', cb)

