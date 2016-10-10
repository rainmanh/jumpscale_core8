from JumpScale.clients.atyourservice.Client import Client


class Factory:

    def __init__(self):
        self.__jslocation__ = "j.clients.atyourservice"

    def get(self, host='localhost', port=6379, unixsocket=None):
        return Client(host=host, port=port, unixsocket=unixsocket)
