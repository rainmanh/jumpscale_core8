from JumpScale import j
import time
import os

class RedisDB():
    def __init__(self):
        self.__jslocation__ = "j.data.redisdb"

    def get(self,path):
        """
        @param path in form of someting:something:...

        @todo (*2*) please describe and give example

        """
        return RedisDBList(path)

    def _test(self):
        llist=self.get("root1:child1")
        
        llist.delete()
        data={"a":"b"}
        llist.set(data,"akey")

        print("iterator:")
        counter=0
        for item in llist:
            counter+=1
            print(item)
        print ("did you see 1 item")
        
        assert(counter==1)

        assert data==llist.get("akey").struct
        assert llist.len()==1
        llist.set(data,"akey")

        assert llist.len()==1
        llist.set(data,"akey2")
        assert llist.len()==2
        llist.delete()
        #now tests around id
        for i in range(10):
            data={"a":"b","id":str(i),"aval":i}
            llist.set(data,"akey%s"%i)

        print (llist.get(id="5"))

        res=llist.find(id="5")

        assert len(res)==1

        res=llist.find(id="5")
        assert res[0].struct["id"]=="5"

        res=llist.find(aval=5)
        assert len(res)==1

class RedisDBObj():
    def __init__(self,llist,path,name="",id=""):
        self._list=llist
        self.db=j.core.db
        self.path=path
        self._struct={}
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
        for item in self._list:
            if item.id==id:
                return item.name                
        raise RuntimeError("Could not find object: %s with id:%s"%(cat,id))

    @property
    def id(self):
        if self._id=="":
            self._id=self.struct["id"]
        return self._id

    @property
    def struct(self):
        data=self.db.hget(self.path,self.name)
        if data==None:
            raise RuntimeError("could not find object %s:%s"%(self.path,self.name))
        obj=j.data.serializer.json.loads(data)
        if "id" in obj:
            self._id=obj["id"]
        if "name" in obj:
            self._name=obj["name"]
        return obj
    
    @struct.setter
    def struct(self,val):
        if j.data.types.dict.check(val)==False:
            raise RuntimeError("only dict supported")
        self.db.hset(self.path,self.name,j.data.serializer.json.dumps(val,sort_keys=True))
        self._list._list={} #will reload

    def __repr__(self):
        return j.data.serializer.json.dumps(self.struct, sort_keys=True, indent=True)

    __str__=__repr__

class RedisDBList:
    def __init__(self,path):
        self.db=j.core.db
        self.path=path
        self._list={}

    @property
    def list(self):
        if self._list=={}:
            keys=self.db.hkeys(self.path)
            keys.sort()
            for name in keys:
                self._list[name]=RedisDBObj(self,self.path,name)
        keys=list(self._list.keys())
        keys.sort()
        res=[]
        for key in keys:
            res.append(self._list[key])
        return res

    def exists(self, name):
        return self.db.hexists(self.path, name)

    def get(self,name="",id=""):
        obj=RedisDBObj(self,self.path,name,id)
        return obj

    def set(self,data,name="", id=""):
        if j.data.types.dict.check(data)==False:
            raise RuntimeError("only dict supported")
        if name=="":
            name = data.get("name", "")
        if name not in data and name!="":
            data["name"]=name
        obj = RedisDBObj(self, self.path, name, id)
        obj.struct=data
        self._list={}
        return obj

    def find(self,name="",id="",**filter):
        if filter=={}:
            #done in special way to be as efficient as possible
            if id=="" and name=="":
                return self.list
            elif id=="":                
                res=[]
                for item in self.list:
                    if item.name==name:
                        import ipdb
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
            res=[]
            for item in self.list:
                if name!="" and item.name!=name:
                    continue
                if id!="" and item.id!=id:
                    continue
                if filter!={}:
                    for key,val in filter.items():
                        found=False
                        if item.struct[key]!=val:
                            found=True
                            continue
                if found==False:
                    res.append(item)
            return res

    def delete(self):
        self.db.delete(self.path)
        self._list={}

    def remove(self, name):
        self.db.hdel(self.path, name)
        self._list.pop(name)

    def __iter__(self):
        return self.list.__iter__()

    def len(self):
        return len(self.list)

    def __bool__(self):
        return self.len() != 0

    def __repr__(self):
        out=""
        for item in self.list:
            out+="%s %s\n"%(self.path,item.name)
        if out=="":
            out="Empty list %s"%(self.path)
        return out

    __str__=__repr__

