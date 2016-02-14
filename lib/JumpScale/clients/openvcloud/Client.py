from JumpScale import j
import time
import os

class DBObj:
    def __init__(self,DB,cat,name="",id=""):
        self.db=j.core.db
        self._DBConnection=DB
        self._obj={}
        self.cat=cat
        self._name=name                
        self._id=id

    @property
    def name(self):
        if self._name=="":
            if self._id=="":
                raise RuntimeError("cannot find id from name, name is not specified.")
            self._name=self._nameFromId(self._id)
        return self._name

    def _nameFromId(self,id):
        for name in self.db.hkeys(self.catkey):
            data= self.db.hget(self.catkey,name)
            if data["id"]==id:
                return name                
        raise RuntimeError("Could not find object: %s with id:%s"%(cat,id))

    @property
    def id(self):
        if self._id=="":
            self._id=self.val["id"]
        return self._id

    @property
    def catkey(self):
        return "openvcloud.%s.%s"%(self._DBConnection.account,self.cat)

    @property
    def val(self):
        data=self.db.hget(self.catkey,self.name)
        if data==None:
            raise RuntimeError("could not find object %s:%s"%(cat,name))
        obj=j.data.serializer.json.loads(data)
        return obj
    
    @setter.obj
    def val(self,val):
        if j.data.types.dict.check(val)==False:
            raise RuntimeError("only dict supported")
        self.db.hset(self.catkey,self.name,j.data.serializer.json.dumps(val,sort_keys=True))
        self._lists.pop(self.catkey)

    def __repr__(self):
        return j.data.serializer.json.dumps(self.val, sort_keys=True, indent=True)

    __str__=__repr__



class DBObjList:
    def __init__(self,DB,cat):
        self.db=j.core.db
        self._DBConnection=DB
        self.cat=cat
        self._list=[]

    @property
    def catkey(self):
        return "openvcloud.%s.%s"%(self._DBConnection.account,self.cat)        

    @property
    def list(self):
        if self._list=[]:
            keys=self.db.hkeys(self.catkey)
            keys.sort()
            for name in keys:
                self._list.append(DBObj(self._DBConnection,self.cat,name))
        return self._list

    def get(self,name="",id=""):
        obj=DBObj(self._DBConnection,self.cat,name,id)
        return obj

    def set(self,data,name=""):
        if name=="":
            name=data["name"]
        if name not in data and name!="":
            data["name"]=name
        obj=DBObj(self._DBConnection,self.cat,name)
        obj.val=data
        return obj

    def find(self,name="",id="",fields={}):
        if fields=={}:
            #done in special way to be as efficient as possible
            if id=="" and name=="":
                return self.list
            elif id=="":                
                res=[]
                for item in self.list:
                    if item.name==name:
                        res.append(item)
            elif name=="":
                res=[]
                for item in self.list:
                    if item.id==id:
                        res.append(item)
                return res
            for item in self.list:
                if item.id==id and item.name==name:
                    return item
            if len(res)>1:
                raise RuntimeError("cannot be more than 1")
            if len(res)==0:
                raise RuntimeError("did not find %s:%s for list:%s"%(name,id,self.cat))
        else:
            #now the slower one but complete one
            for item in self.list:
                if name!="" and item.name!=name:
                    continue
                if id!="" and item.id!=id:
                    continue
                #@todo complete



    def __repr__(self):
        out=""
        for item in self.list:
            out+="%s %s\n"%(self.cat,item.name)
        return out

    __str__=__repr__


class DBConnection:
    #ONLY DEALS WITH CONNECTIONS IN REDIS
    def __init__(self,account):
        self.account=account
        self._lists={}

    @property
    def Spaces(self): #olf space
        if "Space" not in self._lists:
            self._list["Space"]=DBObjList(self,"Space")
        return self._list["Space"]

    @property
    def machines(self):
        if "machine" not in self._lists:
            self._list["machine"]=DBObjList(self,"machine")
        return self._list["machine"]

    @property
    def users(self):
        if "user" not in self._lists:
            self._list["user"]=DBObjList(self,"user")
        return self._list["user"]

    @property
    def accounts(self):
        if "account" not in self._lists:
            self._list["account"]=DBObjList(self,"account")
        return self._list["account"]

    def reset(self,cat=""):
        """
        @param cat == "" then reset all
        """
        from IPython import embed
        print ("DEBUG NOW reset")
        embed()
        





class Factory:
    def __init__(self):
        self.__jslocation__ = "j.clients.openvcloud"
        
        self._clients = {}

    def get(self, account, url="", login="", password=None, secret=None, port=443):
        if url=="":
            
            self._clients[account]= Client(account,url, login, password, secret, port)
            return self._clients[name]
        else:
            self.db.hset("openvcloud.clients",account,j.data.json.dumps([url,login,password,secret,port]))
            self._clients[account]= Client(account,url, login, password, secret, port)
        return self._clients[name]

    @property
    def clients(self):
        if self._clients={}:
            for account in self.db.hkeys("openvcloud.clients"):
                self.get(account)
        return self._clients

def patchMS1(api):
    def portForwardingList(SpaceId):
        url = os.path.join(api.cloudapi.portforwarding._url, 'list')
        return api.cloudapi.portforwarding._session.post(url, {'Spaceid': SpaceId}).json()

    def createPortFoward(SpaceId, protocol, localPort, machineId, publicIp, publicPort):
        url = os.path.join(api.cloudapi.portforwarding._url, 'create')
        req = {'Spaceid': SpaceId,
               'protocol': protocol,
               'localPort': localPort,
               'vmid': machineId,
               'publicIp': publicIp,
               'publicPort': publicPort}
        return api.cloudapi.portforwarding._session.post(url, req).json()

    api.cloudapi.portforwarding.list = portForwardingList
    api.cloudapi.portforwarding.create = createPortFoward

class Client:
    def __init__(self, account,url, login, password=None, secret=None, port=443):
        if not password and not secret:
            raise ValueError("Either secret or password should be given")
        self._accountId = None
        self._userId = None
        self._Accounts={}
        self._url = url
        self._login = login
        self.api = j.clients.portal.get(url, port)
        self.account=account
        self.db=DBConnection(self.account)

        self.__login(password, secret)
        if 'mothership1' in url:
            jsonpath = os.path.join(os.path.dirname(__file__), 'ms1.json')
            self.api.load_swagger(file=jsonpath, group='cloudapi')
            patchMS1(self.api)
            self.locations=["ca1","uk1","be1"]
        else:
            self.api.load_swagger(group='cloudapi')

    @property
    def accountId(self):
        if self._accountId is None:
            self._accountId = self.api.cloudapi.accounts.list()[0]['id']
        return self._accountId

    @property
    def userId(self):
        if self._userId is None:
            from IPython import embed
            print ("DEBUG NOW userId")
            embed()
            
            # self._userId = self.api.cloudapi.accounts.list()[0]['id']
        return self._userId

    @property
    def account(self):
            
            # self._userId = self.api.cloudapi.accounts.list()[0]['id']
        return self._Spaces


    def __login(self, password, secret):
        if not secret:
            secret = self.api.cloudapi.users.authenticate(username=self._login, password=password)
        self.api._session.cookies.clear()  # make sure cookies are empty, clear guest cookie
        self.api._session.cookies['beaker.session.id'] = secret



    def findSize(self, SpaceId, memory=None, vcpus=None):
        for size in self.api.cloudapi.sizes.list(SpaceId=SpaceId):
            if memory and not size['memory'] == memory:
                continue
            if vcpus and not size['vcpus'] == vcpus:
                continue
            return size

    def findImage(self, name):
        for image in self.api.cloudapi.images.list():
            if image['name'] == name:
                return image

    def findSpace(self, name):
        for cs in self.api.cloudapi.Spaces.list():
            if cs['name'] == name:
                return cs


    def getSpace(self,SpaceNameId):


    def __repr__(self):
        out="openvcloud client:%s"%self.name
    __str__=__repr__
        

class Account():
    def __init__(self,client,name):
        self.client=client
        self.name=name
        self._id=""

    @property
    def id(self):
        from IPython import embed
        print ("DEBUG NOW get id for account")
        embed()
        


    @property
    def spaces(self):
        if self._Spaces=={}:
            self._Spaces={}
            #@query API populate 
            from IPython import embed
            print ("DEBUG NOW Spaces")
            embed()

        return self._Spaces


class Space():
    def __init__(self,client,Spaceid):
        self._sizes=None
        self._machines={}
        self.Spaceid=Spaceid
        self.client=client

    @property
    def sizes(self):
        if self._sizes is None:
            from IPython import embed
            print ("DEBUG NOW _sizes")
            embed()
            
            # self._userId = self.api.cloudapi.accounts.list()[0]['id']
        return self._sizes

    @property
    def machines(self):
        if self._machines is None:
            self._machines= self.api.cloudapi.machines.list(SpaceId=self.SpaceId)
        return self._machines

    def findMachine(self, name):
        for machine in:
            if machine['name'] == name:
                return machine

    def __repr__(self):
        out=""
        from IPython import embed
        print ("DEBUG NOW repr")
        embed()

    __str__=__repr__
        


class Machine():
    def __init__(self,client,Space,machineId,machineName):
        self.machineId=machineId
        self.machineName-machineName
        self._sizes=None
        self._machines=None
        self.Space=Space
        self.client=client

    def start(self):
        from IPython import embed
        print ("DEBUG NOW start")
        embed()
        

    def stop(self):
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

        Space = self.api.cloudapi.Spaces.get(SpaceId=machine['Spaceid'])
        publicip = Space['publicipaddress']

        sshport = None
        usedports = set()
        for portforward in self.api.cloudapi.portforwarding.list(SpaceId=machine['Spaceid']):
            if portforward['localIp'] == machineip and int(portforward['localPort']) == 22:
                sshport = int(portforward['publicPort'])
                publicip = portforward['publicIp']
                break
            usedports.add(int(portforward['publicPort']))
        if not sshport:
            sshport = 2200
            while sshport in usedports:
                sshport += 1
            self.api.cloudapi.portforwarding.create(SpaceId=machine['Spaceid'],
                                                    protocol='tcp',
                                                    localPort=22,
                                                    machineId=machine['id'],
                                                    publicIp=publicip,
                                                    publicPort=sshport)
        login = machine['accounts'][0]['login']
        password = machine['accounts'][0]['password']
        return j.tools.executor.getSSHBased(publicip, sshport, login, password)        


    def __repr__(self):
        out=""
        from IPython import embed
        print ("DEBUG NOW repr machine ")
        embed()

    __str__=__repr__
        
