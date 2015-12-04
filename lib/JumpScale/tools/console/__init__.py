from JumpScale import j

def cb():
    from .Console import Console
    return Console()



j.tools._register('console', cb)
