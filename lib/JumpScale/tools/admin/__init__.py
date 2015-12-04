from JumpScale import j


def cb():
    from .Admin import AdminFactory
    return AdminFactory()

j.tools._register('admin', cb)
