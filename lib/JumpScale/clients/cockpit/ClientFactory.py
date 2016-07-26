from JumpScale import j
from JumpScale.clients.cockpit.client import  Client
import requests


class CockpitFactory:

    def __init__(self):
        self.__jslocation__ = "j.clients.cockpit"
        self._clients = {}

    def getClient(self, base_uri, jwt, verify_ssl=True):
        if base_uri not in self._clients:
            self._clients[base_uri] = Client(base_uri, jwt, verify_ssl=verify_ssl)
        return self._clients[base_uri]
