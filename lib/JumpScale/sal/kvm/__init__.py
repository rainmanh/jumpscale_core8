from JumpScale import j

def cb():
    from .KVM import KVM
    return KVM()


j.sal._register('kvm', cb)

