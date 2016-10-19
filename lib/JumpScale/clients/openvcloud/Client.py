from JumpScale import j
import time
import datetime
import os

CACHETIME = 60


class Factory:

    def __init__(self):
        self.__jslocation__ = "j.clients.openvcloud"
        # self._clients = {}

    def get(self, url, login, password=None, secret=None, port=443):
        dbkey = "%s:%s:%s" % (url, login, j.data.hash.md5_string(password))
        # if dbkey in self._clients:
        #     return self._clients[dbkey]
        # else:
        #     cl = Client(url, login, password, secret, port)

        # self._clients[dbkey] = cl

        cl = Client(url, login, password, secret, port)
        return cl

    def getFromService(self, service):
        return self.get(
            url=service.model.data.url,
            login=service.model.data.login,
            password=service.model.data.password)


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

    api.cloudapi.portforwarding.list = patchmethod(
        api.cloudapi.portforwarding.list, {'cloudspaceId': 'cloudspaceid'})
    api.cloudapi.portforwarding.delete = patchmethod(
        api.cloudapi.portforwarding.delete, {'cloudspaceId': 'cloudspaceid'})
    api.cloudapi.portforwarding.create = patchmethod(api.cloudapi.portforwarding.create,
                                                     {'cloudspaceId': 'cloudspaceid', 'machineId': 'vmid'})


class Client:

    def __init__(self, url, login, password=None, secret=None, port=443):
        if not password and not secret:
            raise ValueError("Either secret or password should be given")
        self._url = url
        self._login = login
        # portal support login with md5 of the password
        self._password = j.data.hash.md5_string(password)
        self._secret = secret
        self.api = j.clients.portal.get(url, port)
        # patch handle the case where the connection dies because of inactivity
        self.__patch_portal_client(self.api)

        self._isms1 = 'mothership1' in url
        self.__login(password, secret)
        if self._isms1:
            jsonpath = os.path.join(os.path.dirname(__file__), 'ms1.json')
            self.api.load_swagger(file=jsonpath, group='cloudapi')
            patchMS1(self.api)
        else:
            self.api.load_swagger(group='cloudapi')

        self._basekey = "openvcloud:%s:%s" % (self._url, self._login)
        self._accounts_cache = j.data.redisdb.get(
            "%s:accounts" % (self._basekey), CACHETIME)
        self._locations_cache = j.data.redisdb.get(
            "%s:locations" % (self._basekey), CACHETIME)

    def __patch_portal_client(self, api):
        # try to relogin in the case the connection is dead because of
        # inactivity
        origcall = api.__call__

        def patch_call(that, *args, **kwargs):
            try:
                return origcall(that, *args, **kwargs)
            except ApiError:
                if ApiError.response.status_code == 419:
                    self._login(self._password, self._secret)

        api.__call__ = patch_call

    def __login(self, password, secret):
        if not secret:
            if self._isms1:
                secret = self.api.cloudapi.users.authenticate(
                    username=self._login, password=password)
            else:
                secret = self.api.system.usermanager.authenticate(
                    name=self._login, secret=password)
        # make sure cookies are empty, clear guest cookie
        self.api._session.cookies.clear()
        self.api._session.cookies['beaker.session.id'] = secret

    @property
    def accounts(self):
        if not self._accounts_cache:
            # load from api
            for item in self.api.cloudapi.accounts.list():
                self._accounts_cache.set(item)
        accounts = []
        for account in self._accounts_cache:
            accounts.append(Account(self, account.struct))
        return accounts

    @property
    def locations(self):
        if not self._locations_cache:
            # load from api
            for item in self.api.cloudapi.locations.list():
                self._locations_cache.set(item)
        return [x.struct for x in self._locations_cache]

    def account_get(self, name):
        for account in self.accounts:
            if account.model['name'] == name:
                return account
        raise KeyError("Not account with name %s" % name)

    def reset(self):
        """
        """
        for key in self._accounts_cache.db.keys('%s*' % self._basekey):
            self._accounts_cache.db.delete(key)
        self._accounts_cache.delete()
        self._locations_cache.delete()

    @property
    def login(self):
        return self._login

    def __repr__(self):
        return "openvcloud client: %s" % self._url

    __str__ = __repr__


class Account:

    def __init__(self, client, model):
        self.client = client
        self.model = model
        self.id = model['id']
        self._basekey = "%s:%s" % (self.client._basekey, self.id)
        self._spaces_cache = j.data.redisdb.get(
            "%s:spaces" % self._basekey, CACHETIME)

    @property
    def spaces(self):
        if not self._spaces_cache:
            # load from api
            for item in self.client.api.cloudapi.cloudspaces.list():
                if item['accountId'] == self.model['id']:
                    self._spaces_cache.set(item, id=item['id'])
        spaces = []
        for space in self._spaces_cache:
            spaces.append(Space(self, space.struct))
        return spaces

    def space_get(self, name, location="", create=True,
                  maxMemoryCapacity=-1, maxVDiskCapacity=-1, maxCPUCapacity=-1, maxNASCapacity=-1,
                  maxArchiveCapacity=-1, maxNetworkOptTransfer=-1, maxNetworkPeerTransfer=-1, maxNumPublicIP=-1):
        """
        will get space if it exists,if not will create it
        to retrieve existing one location does not have to be specified

        example: for ms1 possible locations: ca1, eu1 (uk), eu2 (be)

        """
        if not location:
            raise j.exceptions.RuntimeError("Location cannot be empty.")
        for space in self.spaces:
            if space.model['name'] == name and space.model['location'] == location:
                return space
        else:
            if create:
                self.client.api.cloudapi.cloudspaces.create(access=self.client.login,
                                                            name=name,
                                                            accountId=self.id,
                                                            location=location,
                                                            maxMemoryCapacity=maxMemoryCapacity,
                                                            maxVDiskCapacity=maxVDiskCapacity,
                                                            maxCPUCapacity=maxCPUCapacity,
                                                            maxNASCapacity=maxNASCapacity,
                                                            maxArchiveCapacity=maxArchiveCapacity,
                                                            maxNetworkOptTransfer=maxNetworkOptTransfer,
                                                            maxNetworkPeerTransfer=maxNetworkPeerTransfer,
                                                            maxNumPublicIP=maxNumPublicIP)
                self._spaces_cache.delete()
                return self.space_get(name, location, False)
            else:
                raise j.exceptions.RuntimeError(
                    "Could not find space with name %s" % name)

    def create_disk(self, name, gid, description, size=0, type="B"):
        self.client.api.cloudapi.disks.create(accountId=self.id,
                                              name=name,
                                              gid=gid,
                                              description=description,
                                              size=size,
                                              type=type)

    def __str__(self):
        return "openvcloud client account: %(name)s" % (self.model)

    __repr__ = __str__


class Space:

    def __init__(self, account, model):
        self.account = account
        self.client = account.client
        self.model = model
        self.id = model["id"]
        self._basekey = "%s:%s" % (self.account._basekey, self.id)
        self._machines_cache = j.data.redisdb.get(
            "%s:machines" % self._basekey, CACHETIME)
        self._sizes_cache = j.data.redisdb.get(
            "%s:size" % self._basekey, CACHETIME)
        self._images_cache = j.data.redisdb.get(
            "%s:image" % self._basekey, CACHETIME)
        self._portforwardings_cache = j.data.redisdb.get(
            "%s:portforwardings" % self._basekey, CACHETIME)

    def add_external_network(self, name, subnet, gateway, startip, endip, gid, vlan):
        self.client.api.cloudbroker.iaas.addExternalNetwork(cloudspaceId=self.id,
                                                            name=name,
                                                            subnet=subnet,
                                                            getway=gateway,
                                                            startip=startip,
                                                            endip=endip,
                                                            gid=gid,
                                                            vlan=vlan)

    def save(self):
        self.client.api.cloudapi.cloudspaces.update(cloudspaceId=self.model['id'],
                                                    name=self.model['name'],
                                                    maxMemoryCapacity=self.model[
                                                        'maxMemoryCapacity'],
                                                    maxVDiskCapacity=self.model[
                                                        'maxVDiskCapacity'],
                                                    maxCPUCapacity=self.model[
                                                        'maxCPUCapacity'],
                                                    maxNASCapacity=self.model[
                                                        'maxNASCapacity'],
                                                    maxArchiveCapacity=self.model[
                                                        'maxArchiveCapacity'],
                                                    maxNetworkOptTransfer=self.model[
                                                        'maxNetworkOptTransfer'],
                                                    maxNetworkPeerTransfer=self.model[
                                                        'maxNetworkPeerTransfer'],
                                                    maxNumPublicIP=self.model[
                                                        'maxNumPublicIP']
                                                    )

    @property
    def machines(self):
        if not self._machines_cache:
            # load from api
            for item in self.client.api.cloudapi.machines.list(cloudspaceId=self.id):
                self._machines_cache.set(item)
        machines = {}
        for machine in self._machines_cache:
            machines[machine.struct['name']] = Machine(self, machine.struct)
        return machines

    def refresh(self):
        cloudspaces = self.client.api.cloudapi.cloudspaces.list()
        for cloudspace in cloudspaces:
            if cloudspace['id'] == self.id:
                self.model = cloudspace
                break
        else:
            raise j.exceptions.RuntimeError("Cloud space has been deleted")
        self.account._spaces_cache.set(cloudspace, id=self.id)

    def machine_create(self, name, memsize=2, vcpus=1, disksize=10, datadisks=[], image="Ubuntu 15.10 x64"):
        """
        @param memsize in MB or GB
        for now vcpu's is ignored (waiting for openvcloud)

        """
        imageId = self.image_find_id(image)
        sizeId = self.size_find_id(memsize)
        if name in self.machines:
            raise j.exceptions.RuntimeError(
                "Name is not unique, already exists in %s" % self)
        print("cloudspaceid:%s name:%s size:%s image:%s disksize:%s" %
              (self.id, name, sizeId, imageId, disksize))
        self.client.api.cloudapi.machines.create(
            cloudspaceId=self.id, name=name, sizeId=sizeId, imageId=imageId, disksize=disksize, datadisks=datadisks)
        self.reset()
        return self.machines[name]

    @property
    def portforwardings(self):
        if not self._portforwardings_cache:
            # load from api
            for item in self.client.api.cloudapi.portforwarding.list(cloudspaceId=self.id):
                self._portforwardings_cache.set(
                    item, id='%(publicIp)s:%(publicPort)s -> %(localIp)s:%(localPort)s' % item)
        return [x.struct for x in self._portforwardings_cache]

    def isPortforwardExists(self, publicIp, publicport, protocol):
        for pf in self.portforwardings:
            if pf['publicIp'] == publicIp and int(pf['publicPort']) == int(publicport) and pf['protocol'] == protocol:
                return True
        return False

    @property
    def owners(self):
        _owners = []
        for user in self.model['acl']:
            if not user['canBeDeleted']:
                _owners.append(user['userGroupId'])
        return _owners

    @property
    def authorized_users(self):
        return [u['userGroupId'] for u in self.model['acl']]

    def authorize_user(self, username, right="ACDRUX"):
        if username not in self.authorized_users:
            self.client.api.cloudapi.cloudspaces.addUser(
                cloudspaceId=self.id, userId=username, accesstype=right)
            self.refresh()
        return True

    def unauthorize_user(self, username):
        canBeDeleted = [u['userGroupId'] for u in self.model['acl'] if u['canBeDeleted'] is True]

        if username in self.authorized_users and username in canBeDeleted:
            self.client.api.cloudapi.cloudspaces.deleteUser(cloudspaceId=self.id, userId=username, recursivedelete=True)
            self.refresh()
        return True

    def size_find_id(self, memory=None, vcpus=None):
        if memory < 100:
            memory = memory * 1024  # prob given in GB

        sizes = [(item["memory"], item) for item in self.sizes]
        sizes.sort(key=lambda size: size[0])
        sizes.reverse()
        for size, sizeinfo in sizes:
            if memory > size / 1.1:
                return sizeinfo['id']

        raise j.exceptions.RuntimeError("did not find memory size:%s" % memory)

    @property
    def sizes(self):
        if not self._sizes_cache:
            # load from api
            for item in self.client.api.cloudapi.sizes.list(cloudspaceId=self.id):
                self._sizes_cache.set(item)
        return [x.struct for x in self._sizes_cache]

    def image_find_id(self, name):
        name = name.lower()

        for image in self.images:
            imageNameFound = image["name"].lower()
            if imageNameFound.find(name) != -1:
                return image["id"]
        images = [item["name"].lower() for item in self.images]
        raise j.exceptions.RuntimeError(
            "did not find image:%s\nPossible Images:\n%s\n" % (name, images))

    @property
    def images(self):
        if self._images_cache.len() == 0:
            # load from api
            for item in self.client.api.cloudapi.images.list(cloudspaceId=self.id, accountId=self.account.id):
                self._images_cache.set(item)
        return [x.struct for x in self._images_cache]

    def reset(self):
        """
        """
        self._machines_cache.delete()

    def delete(self):
        self.client.api.cloudapi.cloudspaces.delete(cloudspaceId=self.id)

    def __repr__(self):
        return "space: %s (%s)" % (self.model["name"], self.id)

    __str__ = __repr__


class Machine:

    def __init__(self, space, model):
        self.space = space
        self.client = space.client
        self.model = model
        self.id = self.model["id"]
        self.name = self.model["name"]
        self._basekey = "%s:%s" % (self.space._basekey, self.id)
        self._portforwardings_cache = j.data.redisdb.get(
            "%s:portforwardings" % self._basekey, CACHETIME)

    def start(self):
        self.client.api.cloudapi.machines.start(machineId=self.id)

    def stop(self):
        self.client.api.cloudapi.machines.stop(machineId=self.id)

    def restart(self):
        self.client.api.cloudapi.machines.restart(machineId=self.id)

    def delete(self):
        self.client.api.cloudapi.machines.delete(machineId=self.id)

    def create_snapshot(self, name=str(datetime.datetime.now())):
        self.client.api.cloudapi.machines.snapshot(machineId=self.id, name=name)

    def list_snapshots(self):
        return self.client.api.cloudapi.machines.listSnapshots(machineId=self.id)

    def delete_snapshot(self, epoch):
        self.client.api.cloudapi.machines.deleteSnapshot(machineId=self.id, epoch=epoch)

    @property
    def portforwardings(self):
        if not self._portforwardings_cache:
            # load from api
            for item in self.client.api.cloudapi.portforwarding.list(cloudspaceId=self.space.id, machineId=self.id):
                self._portforwardings_cache.set(
                    item, id='%(publicIp)s:%(publicPort)s/%(protocol)s -> %(localIp)s:%(localPort)s/%(protocol)s' % item)
        return [x.struct for x in self._portforwardings_cache]

    def create_portforwarding(self, publicport, localport, protocol='tcp'):
        if protocol not in ['tcp', 'udp']:
            raise j.exceptions.RuntimeError("Protocol for portforward should be tcp or udp not %s" % protocol)
        machineip, _ = self.get_machine_ip()

        if publicport is None:
                unavailable_ports = [int(portinfo['publicPort']) for portinfo in self.space.portforwardings]
                candidate = 2200
                while True:
                    if candidate not in unavailable_ports:
                        publicport = candidate
                        break
                    candidate += 1
        if not self.space.isPortforwardExists(self.space.model['publicipaddress'], publicport, protocol):
            self.client.api.cloudapi.portforwarding.create(cloudspaceId=self.space.id,
                                                           protocol=protocol,
                                                           localPort=localport,
                                                           machineId=self.id,
                                                           publicIp=self.space.model['publicipaddress'],
                                                           publicPort=publicport)
        self.space._portforwardings_cache.delete()
        self._portforwardings_cache.delete()
        return (publicport, localport)

    def delete_portforwarding(self, publicport):
        self.client.api.cloudapi.portforwarding.deleteByPort(cloudspaceId=self.space.id,
                                                             publicIp=self.space.model[
                                                                 'publicipaddress'],
                                                             publicPort=publicport,
                                                             proto='tcp')
        self.space._portforwardings_cache.delete()
        self._portforwardings_cache.delete()

    def delete_portfowarding_by_id(self, pfid):
        self.client.api.cloudapi.portforwarding.delete(cloudspaceid=self.space.id,
                                                       id=pfid)
        self.space._portforwardings_cache.delete()
        self._portforwardings_cache.delete()

    def get_machine_ip(self):
        machine = self.client.api.cloudapi.machines.get(machineId=self.id)

        def getMachineIP(machine):
            if machine['interfaces'][0]['ipAddress'] == 'Undefined':
                machine = self.client.api.cloudapi.machines.get(
                    machineId=self.id)
            return machine['interfaces'][0]['ipAddress']

        machineip = getMachineIP(machine)
        start = time.time()
        timeout = 120
        while machineip == 'Undefined' and start + timeout > time.time():
            time.sleep(5)
            machineip = getMachineIP(machine)
        if machineip == 'Undefined':
            raise j.exceptions.RuntimeError(
                "Could not get IP Address for machine %(name)s" % machine)
        return machineip, machine

    def get_ssh_connection(self, requested_sshport=None):
        """
        Will get a cuisine executor for the machine.
        Will attempt to create a portforwarding
        :return:
        """
        machineip, machine = self.get_machine_ip()
        publicip = self.space.model['publicipaddress']
        while not publicip:
            time.sleep(5)
            self.space.refresh()
            publicip = self.space.model['publicipaddress']

        sshport = None
        usedports = set()
        for portforward in self.space.portforwardings:
            if portforward['localIp'] == machineip and int(portforward['localPort']) == 22:
                sshport = int(portforward['publicPort'])
                break
            usedports.add(int(portforward['publicPort']))
        if not requested_sshport:
            requested_sshport = 2200
            while requested_sshport in usedports:
                requested_sshport += 1
        if not sshport:
            self.create_portforwarding(requested_sshport, 22)
            sshport = requested_sshport
        login = machine['accounts'][0]['login']
        password = machine['accounts'][0]['password']
        # TODO: we need tow work with keys *2
        return j.tools.executor.getSSHBased(publicip, sshport, login, password)

    def __repr__(self):
        return "machine: %s (%s)" % (self.model["name"], self.id)

    __str__ = __repr__
