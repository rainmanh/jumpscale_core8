from JumpScale import j

def cb():
    from .IDGenerator import IDGenerator
    return IDGenerator()


j.tools._register('idgenerator', cb)

