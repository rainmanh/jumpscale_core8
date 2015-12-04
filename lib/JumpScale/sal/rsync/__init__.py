from JumpScale import j

def cb():
    from .RsyncFactory import RsyncFactory
    return RsyncFactory()




#we'll register on both because is as well a tool as a sal

j.sal._register('rsync', cb)
j.tools._register('rsync', cb)