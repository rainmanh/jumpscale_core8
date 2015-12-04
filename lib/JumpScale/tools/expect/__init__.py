from JumpScale import j

def cb():
    from .Expect import ExpectTool
    return ExpectTool()



j.tools._register('expect', cb)
