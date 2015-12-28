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

    def getBaseModel(self):
        return ModelBase

    def getErrorConditionModel(self):
        return ModelErrorCondition

    def getGridModel(self):
        return ModelGrid

    def getGroupModel(self):
        return ModelGroup

    def getJobModel(self):
        return ModelJob

    def getAuditModel(self):
        return ModelAudit

    def getDiskModel(self):
        return ModelDisk

    def getAlertModel(self):
        return ModelAlert

    def getHeartbeatModel(self):
        return ModelHeartbeat

    def getJumpscriptModel(self):
        return ModelJumpscript

    def getMachineModel(self):
        return ModelMachine

    def getNicModel(self):
        return ModelNic

    def getNodeModel(self):
        return ModelNode

    def getProcessModel(self):
        return ModelProcess

    def getTestModel(self):
        return ModelTest

    def getUserModel(self):
        return ModelUser

    def getSessionCacheModel(self):
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

    def get(self, model, guid=None, redis=True, returnObjWhenNonExist=False):
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
            return model.objects.as_pymongo(query)

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
        um = self.getUserModel()
        if um.objects(__raw__={'name': username, 'passwd': {'$in': [passwd, j.tools.hash.md5_string(passwd)]}}):
            return True
        return False
