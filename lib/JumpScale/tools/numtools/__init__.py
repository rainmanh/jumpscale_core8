from JumpScale import j

def cb():
    from .NumTools import NumTools
    return NumTools()


j.tools._register('numtools', cb)
