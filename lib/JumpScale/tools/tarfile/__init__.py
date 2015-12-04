from JumpScale import j

def cb():
    from .TarFile import TarFile
    return TarFile()


j.tools._register('tarfile', cb)
