from JumpScale import j
import time
import os


class Factory:
    def __init__(self):
        self.__jslocation__ = "j.clients.openvcloud"        
        self._clientsdb = j.data.redisdb.get("openvcloud:main:client")
        self._clients={}


    def get(self, account, url="", login="", password=None, secret=None, port=443):
        """
        @param account, specify account name you want to use 
        """
        if account in self._clients:
            return self._clients[account]

        if url=="":            
            data=self._clientsdb.get(name=account)         
            cl= Client(account=data.struct["spaceNameId"], url=data.struct["url"], login=data.struct["login"],\
                password=data.struct["password"], secret=data.struct["secret"], port=data.struct["port"])
        else:
            data={"url":url,"login":login,"password":password,"secret":secret,"port":port}
            self._clientsdb.set(data,name=account)
            cl= Client(account,url, login, password, secret, port)

        self._clients[account]=cl
        return self._clients[account]

    @property
    def clients(self):
        if self._clients=={}:
            for data in self._clientsdb:
                self._clients[data.name]=self.get(data.name)
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
    def __init__(self, account,url, login, password=None, secret=None, port=443):
        if not password and not secret:
            raise ValueError("Either secret or password should be given")
        self._accountId = None
        self._userId = None
        self._url = url
        self._login = login
        self.api = j.clients.portal.get(url, port)
        self._account=account

        self.__login(password, secret)
        if 'mothership1' in url:
            jsonpath = os.path.join(os.path.dirname(__file__), 'ms1.json')
            self.api.load_swagger(file=jsonpath, group='cloudapi')
            patchMS1(self.api)
            self.locations=["ca1","uk1","be1"]
        else:
            self.api.load_swagger(group='cloudapi')

        accounts=self.api.cloudapi.accounts.list()
        found=None
        for accountDict in accounts:
            if accountDict["name"]==account:
                found=accountDict
                continue
        if found==None:
            raise RuntimeError("Could not find account:%s"%account)


        self.accountObj=found
        self.accountName=account
        self.accountId=self.accountObj["id"]        

        self._spaces_cache= j.data.redisdb.get("openvcloud:%s:space"%self.accountName)
        self._sizes_cache= j.data.redisdb.get("openvcloud:%s:size"%self.accountName)
        self._images_cache= j.data.redisdb.get("openvcloud:%s:image"%self.accountName)

        self._spaces={}

    def __login(self, password, secret):
        if not secret:
            secret = self.api.cloudapi.users.authenticate(username=self._login, password=password)
        self.api._session.cookies.clear()  # make sure cookies are empty, clear guest cookie
        self.api._session.cookies['beaker.session.id'] = secret

    @property
    def spaces_cache(self): 
        if self._spaces_cache.len()==0:
            #load from api
            for item in self.api.cloudapi.cloudspaces.list():
                self._spaces_cache.set(item)
        return self._spaces_cache

    @property
    def spaces(self):
        if self._spaces=={}:
            for item in self.spaces_cache:
                self._spaces[item.name]=Space(self,item.struct)
        return self._spaces

    @property
    def sizes(self): 
        if self._sizes_cache.len()==0:
            #load from api
            for item in self.api.cloudapi.sizes.list():
                self._sizes_cache.set(item,name=str(item["memory"]))
        return self._sizes_cache

    @property
    def images(self): 
        if self._images_cache.len()==0:
            #load from api
            for item in self.api.cloudapi.images.list():
                self._images_cache.set(item)
        return self._images_cache

    def reset(self):
        """
        """
        self._spaces_cache.delete()
        self._sizes_cache.delete()
        self._images_cache.delete()
        for space in self.spaces.values():
            space.reset()
        self._spaces={}

    @property
    def user_id(self):
        #@todo is this correct??? think we need to rethink this
        return self.accountId

    def size_find_id(self, memory=None, vcpus=None):
        if memory<100:
            memory=memory*1024 #prob given in GB

        sizes=[item.struct["memory"] for item in self.sizes.list]
        sizes.sort()
        for size in sizes:
            if memory>size*0.9:
                return self.sizes.find(memory=size)[0].struct["id"]

        raise RuntimeError("did not find memory size:%s"%memory)

        # for size in self.api.cloudapi.sizes.list(spaceId=spaceId):
        #     if memory and not size['memory'] == memory:
        #         continue
        #     if vcpus and not size['vcpus'] == vcpus:
        #         continue
        #     return size

    def image_find_id(self, name):
        name=name.lower()
        
        for image in self.images.list:
            imageNameFound=image.struct["name"].lower()
            if imageNameFound.find(name)!=-1:
                return image.struct["id"]
        images=[item.struct["name"].lower() for item in self.images.list]
        raise RuntimeError("did not find image:%s\nPossible Images:\n%s\n"%(name,images))



    def space_get(self,name,location=""): #@todo (*1*) cannot get this to work
        """
        will get space if it exists,if not will create it
        to retrieve existing one location does not have to be specified

        example: for ms1 possible locations: ca1, eur1, uk1

        """
        if name in self.spaces:
            return self.spaces[name]
        else:
            if location=="":
                raise RuntimeError("Location cannot be empty.")
            cloudid=self.api.cloudapi.cloudspaces.create(access=self.accountId,name=name,accountId=self.accountId,location=location)
            self._spaces_cache.delete()
            self._spaces={}
            if not name in self.spaces:
                raise RuntimeError("space not created")
            return self.spaces[name]        

    def __repr__(self):
        out="openvcloud client:%s"%self.accountName
        return out

    __str__=__repr__

class Space():
    def __init__(self,client,model):
        self.client=client
        self.model=model
        self.id=model["id"]
        self._machines_cache= j.data.redisdb.get("openvcloud:%s:%s:machine"%(self.client.accountName,self.model["name"].lower()))
        self._machines={}


    @property
    def machines_cache(self): 
        if self._machines_cache.len()==0:
            #load from api
            for item in self.client.api.cloudapi.machines.list(cloudspaceId=self.id):
                item["name"]=item["name"].lower()
                self._machines_cache.set(item)
        return self._machines_cache

    @property
    def machines(self):
        if self._machines=={}:
            for item in self.machines_cache:
                self._machines[item.name.lower()]=Machine(self,item.struct)
        return self._machines

    def machine_create(self,name,memsize=2,vcpus=1,disksize=10,image="ubuntu 15.04",ssh=True):
        """
        @param memsize in MB or GB
        for now vcpu's is ignored (waiting for openvcloud)

        """
        #@todo (*1*) cannot get this to work
        #@todo (*1*) make sure ubuntu 15.10 is deployed on all locations in ms 1 (not us)
        imageId=self.client.image_find_id(image)
        sizeId=self.client.size_find_id(memsize)
        if name in self.machines:
            raise RuntimeError("Name is not unique, already exists in %s"%self)
        print ("cloudspaceid:%s name:%s size:%s image:%s disksize:%s"%(self.id,name,sizeId,imageId,disksize))
        self.client.api.cloudapi.machines.create(cloudspaceId=self.id,name=name,sizeId=sizeId,imageId=imageId,disksize=disksize)
        self.reset()
        return self.machines[name]


    def reset(self):
        """
        """
        self._machines_cache.delete()
        self._machines={}

    def __repr__(self):
        out="space: %s (%s)"%(self.model["name"],self.id)
        return out

    __str__=__repr__
        


class Machine():
    def __init__(self,space,model):
        self.space=space
        self.client=space.client
        self.model=model
        self.id=self.model["id"]
        self.name=self.model["name"]

    def start(self):
        #@todo (*1*) implement
        from IPython import embed
        print ("DEBUG NOW start")
        embed()
        

    def stop(self):
        #@todo (*1*) implement
        from IPython import embed
        print ("DEBUG NOW stop")
        embed()

    def restart(self):
        self.stop()
        self.start()

    def getSSHConnection(self, machineId):
        """
        Will get a cuisine executor for the machine.
        Will attempt to create a portforwarding

        :param machineId:
        :return:
        """
        #@todo (*1*) test om 3 locations
        
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

        space = self.api.cloudapi.spaces.get(spaceId=machine['spaceId'])
        publicip = space['publicipaddress']

        sshport = None
        usedports = set()
        for portforward in self.api.cloudapi.portforwarding.list(spaceId=machine['spaceId']):
            if portforward['localIp'] == machineip and int(portforward['localPort']) == 22:
                sshport = int(portforward['publicPort'])
                publicip = portforward['publicIp']
                break
            usedports.add(int(portforward['publicPort']))
        if not sshport:
            sshport = 2200
            while sshport in usedports:
                sshport += 1
            self.api.cloudapi.portforwarding.create(spaceId=machine['spaceId'],
                                                    protocol='tcp',
                                                    localPort=22,
                                                    machineId=machine['id'],
                                                    publicIp=publicip,
                                                    publicPort=sshport)
        login = machine['accounts'][0]['login']
        password = machine['accounts'][0]['password']
        return j.tools.executor.getSSHBased(publicip, sshport, login, password)         #@todo we need tow work with keys (*2*)


    def __repr__(self):
        out=""
        from IPython import embed
        print ("DEBUG NOW repr machine ")
        embed()

    __str__=__repr__
        
