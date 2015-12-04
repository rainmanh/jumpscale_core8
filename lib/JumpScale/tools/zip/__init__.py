from JumpScale import j

def cb():
    from .ZipFile import ZipFile
    return ZipFile()


j.tools._register('zipfile', cb)
