from JumpScale.clients.itsyouonline import Client


class ClientFactory:

    def __init__(self):
        self.__jslocation__ = 'j.clients.itsyouonline'

    def get(self):
        return Client()
