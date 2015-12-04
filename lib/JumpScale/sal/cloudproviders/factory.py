from .amazon import AmazonProvider
from .digitalocean import DigitalOcean

from sal.base.SALObject import SALObject

class Factory(SALObject):

    def get(self, provider):
        '''Gets an instance of the cloud provider class
        @param provider: sting represents provider type, can be GOOGLE, AMAZON, DIGITALOCEAN, ...
        '''
        providers = {'AMAZON': AmazonProvider, 'DIGITALOCEAN': DigitalOcean}
        return providers[provider]()