from JumpScale import j

def cb():
    import JumpScale.grid.gevent
    import JumpScale.baselib.key_value_store
    import JumpScale.baselib.serializers
    from .ZDaemonFactory import ZDaemonFactory
    return ZDaemonFactory()


j.core._register('zdaemon', cb)


j.servers._register('zdaemon', cb)
