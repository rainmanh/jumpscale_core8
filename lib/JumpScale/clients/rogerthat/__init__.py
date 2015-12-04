from JumpScale import j

def cb():
    from .rogerthat import RogerthatFactory
    return RogerthatFactory()


j.clients._register('rogerthat', cb)
