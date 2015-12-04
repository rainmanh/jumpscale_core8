from JumpScale import j

def cb():
    from .QSocketServer import QSocketServer, QSocketServerFactory
    return QSocketServerFactory()


j.servers._register('socketserver', cb)
