from JumpScale import j

def cb():
    from .MongoDBClient import MongoDBClient
    return MongoDBClient()


j.clients._register('mongodb', cb)


