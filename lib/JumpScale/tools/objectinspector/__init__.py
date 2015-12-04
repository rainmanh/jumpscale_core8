from JumpScale import j

def cb():
    from .ObjectInspector import ObjectInspector
    return ObjectInspector()


j.tools._register('objectinspector', cb)
