from JumpScale import j


def action(service):
    s = j.atyourservice.getServiceFromKey(service)
    s.monitor()
