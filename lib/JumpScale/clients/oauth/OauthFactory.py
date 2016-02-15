import os


    
from JumpScale import j
from OauthInstance import *

class OauthFactory(object):

    def __init__(self):
        self.__jslocation__ = "j.clients.oauth"
        j.logger.consolelogCategories.append('oauth')

    def get(self, addr='', accesstokenaddr='', id='', secret='', scope='', redirect_url='', user_info_url='', logout_url='', instance='github'):        
        return OauthInstance(addr, accesstokenaddr, id, secret, scope, redirect_url, user_info_url, logout_url, instance)

    def log(self,msg,category='',level=5):
        category = 'oauth.%s'%category
        category = category.rstrip('.')
        j.logger.log(msg,category=category,level=level)