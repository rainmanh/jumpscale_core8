from JumpScale import j
import time
import os


class Factory:
    def __init__(self):
        self.__jslocation__ = "j.clients.openvcloud"

    def get(self, url, login, password=None, secret=None, port=443):
        return Client(url, login, password, secret, port)

def patchMS1(api):
    def portForwardingList(cloudspaceId):
        url = os.path.join(api.cloudapi.portforwarding._url, 'list')
        return api.cloudapi.portforwarding._session.post(url, {'cloudspaceid': cloudspaceId}).json()

    def createPortFoward(cloudspaceId, protocol, localPort, machineId, publicIp, publicPort):
        url = os.path.join(api.cloudapi.portforwarding._url, 'create')
        req = {'cloudspaceid': cloudspaceId,
               'protocol': protocol,
               'localPort': localPort,
               'vmid': machineId,
               'publicIp': publicIp,
               'publicPort': publicPort}
        return api.cloudapi.portforwarding._session.post(url, req).json()

    api.cloudapi.portforwarding.list = portForwardingList
    api.cloudapi.portforwarding.create = createPortFoward

class Client:
    def __init__(self, url, login, password=None, secret=None, port=443):
        if not password and not secret:
            raise ValueError("Either secret or password should be given")
        self._url = url
        self._login = login
        self.api = j.clients.portal.get(url, port)
        self.__login(password, secret)
        if 'mothership1' in url:
            patchMS1(self.api)

    def __login(self, password, secret):
        if not secret:
            secret = self.api.cloudapi.users.authenticate(username=self._login, password=password)
        self.api._session.cookies.clear()  # make sure cookies are empty, clear guest cookie
        self.api._session.cookies['beaker.session.id'] = secret

    def findSize(self, memory=None, vcpus=None):
        for size in self.api.cloudapi.sizes.list():
            if memory and not size['memory'] == memory:
                continue
            if vcpus and not size['vcpus'] == vcpus:
                continue
            return size

    def findImage(self, name):
        for image in self.api.cloudapi.images.list():
            if image['name'] == name:
                return image

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

