from JumpScale import j

def cb():
    from .OSTicketFactory import OSTicketFactory
    return OSTicketFactory()


j.clients._register('osticket', cb)
