from JumpScale import j

def cb():
    import JumpScale.baselib.code
    from .OSIS import OSIS
    return OSIS()

j.core._register('osismodel', cb)
