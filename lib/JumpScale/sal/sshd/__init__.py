from JumpScale import j

def cb():
    from .SSHD import SSHD
    return SSHD()


j.sal._register('sshd', cb)