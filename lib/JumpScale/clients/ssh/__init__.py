from JumpScale import j


def cb():
    from .SSHClient import SSHClientFactory
    return SSHClientFactory()


j.clients._register('ssh', cb)
