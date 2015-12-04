from JumpScale import j

def cb():
    from .dnsmasq import DNSMasq
    return DNSMasq()


j.sal._register('dnsmasq', cb)
