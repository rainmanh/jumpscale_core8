from JumpScale import j

def cb():
    from .ImageLib import ImageLib
    return ImageLib()


j.tools._register('imagelib', cb)
