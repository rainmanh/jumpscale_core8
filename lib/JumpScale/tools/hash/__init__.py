from JumpScale import j

def cb():
    from .HashTool import HashTool
    return HashTool()


j.tools._register('hash', cb)
