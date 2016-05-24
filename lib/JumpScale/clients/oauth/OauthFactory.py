import os



from JumpScale import j
from OauthInstance import *

class OauthFactory:

    def __init__(self):
        self.__jslocation__ = "j.clients.oauth"
        self.logger = j.logger.get('j.clients.oauth')

    def get(self, addr='', accesstokenaddr='', id='', secret='', scope='', redirect_url='', user_info_url='', logout_url='', instance='github'):
        return OauthInstance(addr, accesstokenaddr, id, secret, scope, redirect_url, user_info_url, logout_url, instance)
