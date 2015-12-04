from JumpScale import j

def cb():
    from .HttpClient import HttpClient
    return HttpClient()


j.clients._register('http', cb)
