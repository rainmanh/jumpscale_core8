from JumpScale import j

def cb():
    from .Samba import Samba
    return Samba()


j.sal._register('samba', cb)