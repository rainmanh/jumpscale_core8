from JumpScale import j

from Models import *

import mongoengine

if not j.sal.process.checkProcessRunning('mongod'):
    j.sal.process.execute(
        "mongod --fork --logpath /opt/jumpscale8/var/mongodb.log")

try:
    mongoengine.connection.get_connection()
except:
    mongoengine.connect(db='jumpscale_system')


class BaseModelFactory():

    def __init__(self):
        self.__jslocation__ = "j.data.models"

    DoesNotExist = DoesNotExist

    @property
    def Machine(self):
        return ModelMachine

    @property
    def Base(self):
        return ModelBase

    @property
    def ErrorCondition(self):
        return ModelErrorCondition

    @property
    def Grid(self):
        return ModelGrid

    @property
    def Group(self):
        return ModelGroup

    @property
    def Job(self):
        return ModelJob

    @property
    def Command(self):
        return ModelCommand

    @property
    def Audit(self):
        return ModelAudit

    @property
    def Disk(self):
        return ModelDisk

    @property
    def Alert(self):
        return ModelAlert

    @property
    def Heartbeat(self):
        return ModelHeartbeat

    @property
    def Jumpscript(self):
        return ModelJumpscript

    @property
    def Machine(self):
        return ModelMachine

    @property
    def Nic(self):
        return ModelNic

    @property
    def Node(self):
        return ModelNode

    @property
    def Process(self):
        return ModelProcess

    @property
    def Test(self):
        return ModelTest

    @property
    def User(self):
        return ModelUser

    @property
    def SessionCache(self):
        return ModelSessionCache

    def getKey(self, modelname, guid):
        """
        @return hsetkey,key
        """
        ttype = modelname.split(".")[-1].replace("Model", "").lower()
        key = "models.%s" % ttype
        key = '%s_%s' % (key, guid)
        key = key.encode('utf-8')
        return key

    def get(self, model, guid=None, redis=False, returnObjWhenNonExist=False):
        """
        default needs to be in redis, need to mention if not
        """
        # model is not a class its really the object

        if redis:
            if guid == None:
                guid = model.guid
            modelraw = j.core.db.get(self.getKey(model._class_name, guid))
            if modelraw:
                modelraw = modelraw.decode()
                model = model.from_json(modelraw)
                model._redis = True
                return model
            else:
                res = None
        else:
            if guid is None:
                raise RuntimeError("guid cannot be None")
            try:
                res = model.objects.get(guid=guid)
            except DoesNotExist:
                res = None

        if returnObjWhenNonExist and res is None:
            return model
        return res

    def set(self, modelobject, redis=True):
        key = self.getKey(modelobject._class_name, modelobject.guid)
        meta = modelobject._meta['indexes']
        expirey = meta[0].get('expireAfterSeconds', None) if meta else None
        modelraw = json.dumps(modelobject.to_dict())
        j.core.db.set(key, modelraw)
        if expirey:
            j.core.db.expire(key, expirey)
        return modelobject

    def getset(self, modelobject, redis=True):
        key = self.getKey(modelobject._class_name, modelobject.guid)
        if redis:
            model = self.get(modelobject, redis=True)
            if model == None:
                self.set(modelobject, redis=True)
                model = modelobject
            model._redis = True
            return model
        else:
            raise RuntimeError("not implemented")

    def find(self, model, query, redis=False):
        if redis:
            raise RuntimeError("not implemented")
        else:
            return model.objects(__raw__=query)

    def delete(self, model, key, redis=True):
        raise RuntimeError("not implemented")
        pass

    def exists(self, model, guid=None, redis=True):
        if redis:
            if guid == None:
                guid = model.guid
            modelname = model._class_name
            key = self.getKey(modelname, guid)
            if j.core.db.exists('%s_%s' % (key, guid)):
                return True
            else:
                return False
        else:
            if guid == None:
                raise RuntimeError("guid cannot be None")
            try:
                model.objects.get(guid=guid)
            except DoesNotExist:
                return False

    def authenticate(self, username, passwd):
        um = self.User
        if um.objects(__raw__={'name': username, 'passwd': {'$in': [passwd, j.tools.hash.md5_string(passwd)]}}):
            return True
        return False
