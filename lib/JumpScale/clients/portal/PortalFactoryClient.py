##from ActorsLoaderRemote import ActorsLoaderRemote
from JumpScale.clients.portal.PortalClient import Resource
#from .PortalServer import PortalServer
#from .PortalClient import PortalClient
#from .PortalClient2 import Resource
import time
#from ActorLoaderLocal import *


from JumpScale import j


class Group():
    pass


class PortalFactoryClient(object):
    def __init__(self):
        self.__jslocation__ = "j.clients.portal"
        self._portalClients = {}

    def getByInstance(self, instance=None):
        if not instance:
            instance = j.application.hrdinstance.get('portal.connection')
        hrd = j.application.getAppInstanceHRD(name="portal_client", instance=instance)
        addr = hrd.get('param.addr')
        port = hrd.getInt('param.port')
        secret = hrd.getStr('param.secret')
        return self.get(addr, port, secret)

    def get(self, ip="localhost", port=82, secret=None):
        return Resource(ip, port, secret, "/restmachine")
