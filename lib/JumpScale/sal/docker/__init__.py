from JumpScale import j

def cb():
    from .Docker2 import Docker2
    return Docker2()


j.sal._register('docker', cb)

