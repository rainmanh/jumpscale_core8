from JumpScale import j

def cb():
    from .GraphiteClient import GraphiteClient
    return GraphiteClient()


j.clients._register('graphite', cb)


