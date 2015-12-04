from JumpScale import j

def cb():
    from .text import Text
    return Text


j.tools._register('text', cb)
