from JumpScale import j

def cb():
    from .PostgresqlFactory import PostgresqlFactory
    return PostgresqlFactory()


j.clients._register('postgres', cb)
