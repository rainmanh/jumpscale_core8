from JumpScale import j

def cb():
    from .PackInCode import packInCodeFactory
    return packInCodeFactory()


j.tools._register('packInCode', cb)
