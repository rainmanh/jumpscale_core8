from JumpScale import j

def cb():
    from .MySQLFactory import MySQLFactory
    return MySQLFactory()


j.clients._register('mysql', cb)
