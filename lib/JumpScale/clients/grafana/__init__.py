from JumpScale import j

def cb():
    from .grafana import GrafanaFactory
    return GrafanaFactory()


j.clients._register('grafana', cb)

