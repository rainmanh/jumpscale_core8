from JumpScale import j

def cb():
    from .Elasticsearch import ElasticsearchFactory
    return ElasticsearchFactory()


j.clients._register('elasticsearch', cb)
