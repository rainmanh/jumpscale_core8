from JumpScale import j
import time
import os


class Factory:
    def __init__(self):
        self.__jslocation__ = "j.clients.openvcloud"        
        self._clientsdb = j.data.redisdb.get("openvcloud:main:client")
        self._clients = {}

    def get(self, url, login, password=None, secret=None, port=443):
        dbkey = "%s:%s" % (url, login)
        if dbkey in self._clients:
            return self._clients[dbkey]
        if self._clientsdb.exists(dbkey):
            cl = self.get_from_db(dbkey)
        else:
            data = {"url": url, "login" : login, "password": password, "secret": secret, "port": port}
            self._clientsdb.set(data, name=dbkey)
            cl = Client(url, login, password, secret, port)

        self._clients[dbkey] = cl
        return cl

    def get_from_db(self, dbkey):
        data = self._clientsdb.get(name=dbkey)
        return Client(url=data.struct["url"], login=data.struct["login"], password=data.struct["password"],
                    secret=data.struct["secret"], port=data.struct["port"])

    @property
    def clients(self):
        if self._clients == {}:
            for data in self._clientsdb:
                self._clients[data.name] = self.get_from_db(data.name)
        return self._clients


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


    api.cloudapi.portforwarding.list = patchmethod(api.cloudapi.portforwarding.list, {'cloudspaceId': 'cloudspaceId'})
    api.cloudapi.portforwarding.create = patchmethod(api.cloudapi.portforwarding.create,
                                                     {'cloudspaceId': 'cloudspaceId', 'machineId': 'vmid'})

class Client:
    def __init__(self, url, login, password=None, secret=None, port=443):
        if not password and not secret:
            raise ValueError("Either secret or password should be given")
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

        self._basekey = "openvcloud:%s:%s" % (self._url, self._login)
        self._accounts_cache = j.data.redisdb.get("%s:accounts"% (self._basekey))
        self._locations_cache = j.data.redisdb.get("%s:locations"% (self._basekey))

    def __login(self, password, secret):
        if not secret:
            secret = self.api.cloudapi.users.authenticate(username=self._login, password=password)
        self.api._session.cookies.clear()  # make sure cookies are empty, clear guest cookie
        self.api._session.cookies['beaker.session.id'] = secret


    @property
    def accounts(self):
        if not self._accounts_cache:
            #load from api
            for item in self.api.cloudapi.accounts.list():
                self._accounts_cache.set(item, name=str(item["name"]))
        accounts = []
        for account in self._accounts_cache:
            accounts.append(Account(self, account.struct))
        return accounts

    @property
    def locations(self):
        if not self._locations_cache:
            #load from api
            for item in self.api.cloudapi.locations.list():
                self._locations_cache.set(item, name=str(item["locationCode"]))
        return self._locations_cache

    def account_get(self, name):
        for account in self.accounts:
            if account.model['name'] == name:
                return account
        raise KeyError("Not account with name %s" % name)


    def reset(self):
        """
        """
        for key in self._accounts_cache.db.keys('%s*' % self._basekey):
            print(key)
            self._accounts_cache.db.delete(key)

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
        self._spaces_cache = j.data.redisdb.get("%s:spaces" % self._basekey)

    @property
    def spaces(self):
        if not self._spaces_cache:
            #load from api
            for item in self.client.api.cloudapi.cloudspaces.list():
                if item['accountId'] == self.model['id']:
                    self._spaces_cache.set(item)
        spaces = []
        for space in self._spaces_cache:
            spaces.append(Space(self, space.struct))
        return spaces

    def space_get(self, name, location="", create=True):
        """
        will get space if it exists,if not will create it
        to retrieve existing one location does not have to be specified

        example: for ms1 possible locations: ca1, eu1 (uk), eu2 (be)

        """
        if not location:
            raise RuntimeError("Location cannot be empty.")
        for space in self.spaces:
            if space.model['name'] == name and space.model['location'] == location:
                return space
        else:
            if create:
                self.client.api.cloudapi.cloudspaces.create(access=self.client.login,
                                                            name=name,
                                                            accountId=self.id,
                                                            location=location)
                self._spaces_cache.delete()
                return self.space_get(name, location, False)
            else:
                raise RuntimeError("Could not find space with name %s" % name)

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
        self._machines_cache = j.data.redisdb.get("%s:machines" % self._basekey)
        self._sizes_cache = j.data.redisdb.get("%s:size"%self._basekey)
        self._images_cache = j.data.redisdb.get("%s:image"%self._basekey)

    @property
    def machines(self):
        if not self._machines_cache:
            #load from api
            for item in self.client.api.cloudapi.machines.list(cloudspaceId=self.id):
                self._machines_cache.set(item)
        machines = {}
        for machine in self._machines_cache:
            machines[machine.struct['name']] = Machine(self, machine.struct)
        return machines

    def machine_create(self, name, memsize=2, vcpus=1, disksize=10, image="ubuntu 15.04", ssh=True):
        """
        @param memsize in MB or GB
        for now vcpu's is ignored (waiting for openvcloud)

        """
        imageId = self.image_find_id(image)
        sizeId = self.size_find_id(memsize)
        if name in self.machines:
            raise RuntimeError("Name is not unique, already exists in %s"%self)
        print ("cloudspaceid:%s name:%s size:%s image:%s disksize:%s"%(self.id,name,sizeId,imageId,disksize))
        self.client.api.cloudapi.machines.create(cloudspaceId=self.id, name=name, sizeId=sizeId, imageId=imageId, disksize=disksize)
        self.reset()
        return self.machines[name]

    def size_find_id(self, memory=None, vcpus=None):
        if memory<100:
            memory=memory*1024 #prob given in GB

        sizes=[item.struct["memory"] for item in self.sizes.list]
        sizes.sort()
        for size in sizes:
            if memory>size*0.9:
                return self.sizes.find(memory=size)[0].struct["id"]

        raise RuntimeError("did not find memory size:%s"%memory)

    @property
    def sizes(self):
        if not self._sizes_cache:
            #load from api
            for item in self.client.api.cloudapi.sizes.list(cloudspaceId=self.id):
                self._sizes_cache.set(item,name=str(item["memory"]))
        return self._sizes_cache

    def image_find_id(self, name):
        name=name.lower()

        for image in self.images.list:
            imageNameFound=image.struct["name"].lower()
            if imageNameFound.find(name)!=-1:
                return image.struct["id"]
        images=[item.struct["name"].lower() for item in self.images.list]
        raise RuntimeError("did not find image:%s\nPossible Images:\n%s\n"%(name,images))

    @property
    def images(self):
        if self._images_cache.len()==0:
            #load from api
            for item in self.client.api.cloudapi.images.list(cloudspaceId=self.id, accountId=self.account.id):
                self._images_cache.set(item)
        return self._images_cache

    def reset(self):
        """
        """
        self._machines_cache.delete()

    def __repr__(self):
        return "space: %s (%s)"%(self.model["name"],self.id)

    __str__=__repr__
        

class Machine:
    def __init__(self, space, model):
        self.space = space
        self.client = space.client
        self.model = model
        self.id = self.model["id"]
        self.name = self.model["name"]

    def start(self):
        self.client.api.cloudapi.machines.start(machineId=self.id)

    def stop(self):
        self.client.api.cloudapi.machines.stop(machineId=self.id)

    def restart(self):
        self.client.api.cloudapi.machines.restart(machineId=self.id)

    def getSSHConnection(self):
        """
        Will get a cuisine executor for the machine.
        Will attempt to create a portforwarding
        :return:
        """

        machine = self.client.api.cloudapi.machines.get(machineId=self.id)

        def getMachineIP(machine):
            if machine['interfaces'][0]['ipAddress'] == 'Undefined':
                machine = self.client.api.cloudapi.machines.get(machineId=self.id)
            return machine['interfaces'][0]['ipAddress']

        machineip = getMachineIP(machine)
        start = time.time()
        timeout = 60
        while machineip == 'Undefined' and start + timeout < time.time():
            time.sleep(5)
            machineip = getMachineIP(machine)
        if not machineip:
            raise RuntimeError("Could not get IP Address for machine %(name)s" % machine)

        publicip = self.space.model['publicipaddress']

        sshport = None
        usedports = set()
        for portforward in self.client.api.cloudapi.portforwarding.list(cloudspaceId=self.space.id):
            if portforward['localIp'] == machineip and int(portforward['localPort']) == 22:
                sshport = int(portforward['publicPort'])
                publicip = portforward['publicIp']
                break
            usedports.add(int(portforward['publicPort']))
        if not sshport:
            sshport = 2200
            while sshport in usedports:
                sshport += 1
            self.client.api.cloudapi.portforwarding.create(cloudspaceId=self.space.id,
                                                           protocol='tcp',
                                                           localPort=22,
                                                           machineId=machine['id'],
                                                           publicIp=publicip,
                                                           publicPort=sshport)
        login = machine['accounts'][0]['login']
        password = machine['accounts'][0]['password']
        return j.tools.executor.getSSHBased(publicip, sshport, login, password)         #@todo we need tow work with keys (*2*)

    def __repr__(self):
        return "machine: %s (%s)"%(self.model["name"], self.id)

    __str__=__repr__
