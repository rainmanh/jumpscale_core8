from JumpScale import j
import json
import requests
import sys

class SkyDNSClientFactory():
    def __init__(self):
        self.__jslocation__ = "j.clients.skydns"

    def get(self, baseurl, username=None, password=None):
        """
        baseurl: str, url of the etcd for skydns e.g: https://dns1.aydo.com/etcd
        """
        return SkyDNSClient(baseurl, username, password)

class SkyDNSClient():
    def __init__(self, baseurl='', username=None, password=None):
        self.baseurl = ('%s/v2/keys/skydns/' % baseurl)
        self.username = username
        self.password = password
        
    def read(self, endpoint):
        link = self.mkurl(endpoint)
        print('[+] %s' % link)
        
        if self.username:
            r = requests.get(link, auth=(self.username, self.password))
            
        else:
            r = requests.get(link)
        
        if r.status_code == 401:
            return {'not authorized'}
        
        return r.json()

    def write(self, endpoint, data):
        link = self.mkurl(endpoint)
        print('[+] %s' % link)
        
        payload = {'value': json.dumps(data)}
        
        if self.username:
            r = requests.put(link, data=payload, auth=(self.username, self.password))
        else:
            r = requests.put(link, data=payload)
        
        if r.status_code == 401:
            return {'not authorized'}
        
        return r.json()

    def mkurl(self, endpoint, complement=''):
        return '%s%s' % (self.baseurl, endpoint)

    def _hostKey(self, host):
        items = host.split('.')
        items = list(reversed(items))
        key = "/".join(items)
        return key
    
    

    def getConfig(self):
        return self.read('config')
        
    def setConfig(self, config):
        self.write('config', config)
        return self.getConfig()
    
    # valid for AAAA and CNAME btw
    def setRecordA(self, name, target, priority=20):
        key = self._hostKey(name)
        self.write(key, {'host': target, 'priority': priority})
        return self.read(key)
