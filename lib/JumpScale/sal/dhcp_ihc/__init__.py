from JumpScale import j

def cb():
    from .DHCP import DHCP
    return DHCP()


j.sal._register('dhcp_ihc', cb)
