from JumpScale import j
import time
import os


class Factory:
    def __init__(self):
        self.__jslocation__ = "j.clients.openvcloud"

    def get(self, url, login, password=None, secret=None, port=443):
        return Client(url, login, password, secret, port)

def patchMS1(api):
    def patchmethod(method, argmap):
        def wrapper(**kwargs):
            for oldkey, newkey in argmap.items():
                if oldkey in kwargs:
                    value = kwargs.pop(oldkey)
                    kwargs[newkey] = value
            return method(**kwargs)
        wrapper.__doc__ = method.__doc__
        return wrapper


    api.cloudapi.portforwarding.list = patchmethod(api.cloudapi.portforwarding.list, {'cloudspaceId': 'cloudspaceid'})
    api.cloudapi.portforwarding.create = patchmethod(api.cloudapi.portforwarding.create,
                                                     {'cloudspaceId': 'cloudspaceid', 'machineId': 'vmid'})

class Client:
    def __init__(self, url, login, password=None, secret=None, port=443):
        if not password and not secret:
            raise ValueError("Either secret or password should be given")
        self._accountId = None
        self._url = url
        self._login = login
        self.api = j.clients.portal.get(url, port)
        self.__login(password, secret)
        if 'mothership1' in url:
            jsonpath = os.path.join(os.path.dirname(__file__), 'ms1.json')
            self.api.load_swagger(file=jsonpath, group='cloudapi')
            patchMS1(self.api)
        else:
            self.api.load_swagger(group='cloudapi')

    @property
    def accountId(self):
        if self._accountId is None:
            self._accountId = self.api.cloudapi.accounts.list()[0]['id']
        return self._accountId

    def __login(self, password, secret):
        if not secret:
            secret = self.api.cloudapi.users.authenticate(username=self._login, password=password)
        self.api._session.cookies.clear()  # make sure cookies are empty, clear guest cookie
        self.api._session.cookies['beaker.session.id'] = secret

    def findSize(self, cloudspaceId, memory=None, vcpus=None):
        for size in self.api.cloudapi.sizes.list(cloudspaceId=cloudspaceId):
            if memory and not size['memory'] == memory:
                continue
            if vcpus and not size['vcpus'] == vcpus:
                continue
            return size

    def findImage(self, name):
        for image in self.api.cloudapi.images.list():
            if image['name'] == name:
                return image

    def findCloudSpace(self, name):
        for cs in self.api.cloudapi.cloudspaces.list():
            if cs['name'] == name:
                return cs

    def findMachine(self, cloudspaceId, name):
        for machine in self.api.cloudapi.machines.list(cloudspaceId=cloudspaceId):
            if machine['name'] == name:
                return machine

    def getSSHConnection(self, machineId):
        """
        Will get a cuisine executor for the machine.
        Will attempt to create a portforwarding

        :param machineId:
        :return:
        """
        machine = self.api.cloudapi.machines.get(machineId=machineId)

        def getMachineIP(machine):
            if machine['interfaces'][0]['ipAddress'] == 'Undefined':
                machine = self.api.cloudapi.machines.get(machineId=machineId)
            return machine['interfaces'][0]['ipAddress']

        machineip = getMachineIP(machine)
        start = time.time()
        timeout = 60
        while machineip == 'Undefined' and start + timeout < time.time():
            time.sleep(5)
            machineip = getMachineIP(machine)
        if not machineip:
            raise RuntimeError("Could not get IP Address for machine %(name)s" % machine)

        cloudspace = self.api.cloudapi.cloudspaces.get(cloudspaceId=machine['cloudspaceid'])
        publicip = cloudspace['publicipaddress']

        sshport = None
        usedports = set()
        for portforward in self.api.cloudapi.portforwarding.list(cloudspaceId=machine['cloudspaceid']):
            if portforward['localIp'] == machineip and int(portforward['localPort']) == 22:
                sshport = int(portforward['publicPort'])
                publicip = portforward['publicIp']
                break
            usedports.add(int(portforward['publicPort']))
        if not sshport:
            sshport = 2200
            while sshport in usedports:
                sshport += 1
            self.api.cloudapi.portforwarding.create(cloudspaceId=machine['cloudspaceid'],
                                                    protocol='tcp',
                                                    localPort=22,
                                                    machineId=machine['id'],
                                                    publicIp=publicip,
                                                    publicPort=sshport)
        login = machine['accounts'][0]['login']
        password = machine['accounts'][0]['password']
        return j.tools.executor.getSSHBased(publicip, sshport, login, password)
